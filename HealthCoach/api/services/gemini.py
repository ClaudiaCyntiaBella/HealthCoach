"""Integrasi Gemini Vision untuk identifikasi makanan dari beberapa sudut."""

import json
import logging
import time
from dataclasses import dataclass

from django.conf import settings
from google import genai
from google.genai import types

from api.exceptions import (
    GeminiConfigurationError,
    GeminiResponseError,
    GeminiTimeoutError,
    GeminiUnavailableError,
)


logger = logging.getLogger(__name__)

VISION_PROMPT = """
Anda adalah sistem identifikasi makanan untuk aplikasi HealthCoach.

Semua foto yang diberikan merupakan beberapa sudut dari SATU makanan atau satu
porsi yang sama. Gabungkan informasi dari seluruh foto untuk membuat satu hasil.
Jangan mengarang nilai nutrisi, diagnosis, atau rekomendasi diet.

Tugas:
1. Tentukan nama makanan utama dalam Bahasa Indonesia.
2. Catat komponen yang benar-benar terlihat dan yang hanya diperkirakan.
3. Berikan keyakinan: tinggi, sedang, atau rendah.
4. Jika objek bukan makanan atau tidak cukup jelas, gunakan food_name null dan
   jelaskan alasannya pada notes.

Kembalikan JSON valid saja:
{
  "food_name": "nama makanan atau null",
  "confidence": "tinggi | sedang | rendah",
  "ingredients": [
    {"name": "nama bahan", "visible": true, "confidence": "tinggi"}
  ],
  "notes": "catatan singkat"
}
""".strip()


@dataclass(frozen=True)
class FoodIdentification:
    food_name: str | None
    confidence: str
    ingredients: list[dict]
    notes: str

    @property
    def status(self) -> str:
        return "IDENTIFIED" if self.food_name else "UNKNOWN"

    def to_dict(self) -> dict:
        return {
            "food_name": self.food_name,
            "identification_status": self.status,
            "confidence": self.confidence,
            "ingredients": self.ingredients,
            "notes": self.notes,
        }


def _parse_json_response(response_text: str | None) -> dict:
    if not response_text:
        raise GeminiResponseError()

    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    try:
        result = json.loads(cleaned.strip())
    except (json.JSONDecodeError, TypeError) as exc:
        raise GeminiResponseError() from exc

    if not isinstance(result, dict):
        raise GeminiResponseError()
    return result


def _create_client():
    if not settings.GEMINI_API_KEY:
        raise GeminiConfigurationError()

    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=settings.GEMINI_TIMEOUT_SECONDS * 1000),
    )


def _generate_json(contents) -> dict:
    client = _create_client()
    models = tuple(
        dict.fromkeys(
            model
            for model in (settings.GEMINI_MODEL, settings.GEMINI_FALLBACK_MODEL)
            if model
        )
    )
    last_error = None

    for index, model in enumerate(models):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                ),
            )
            return _parse_json_response(response.text)
        except GeminiResponseError:
            raise
        except Exception as exc:  # SDK memiliki beberapa kelas error per versi.
            last_error = exc
            message = str(exc).lower()
            logger.warning("Gemini gagal menggunakan model %s: %s", model, type(exc).__name__)

            if "timeout" in message or "deadline" in message:
                if index == len(models) - 1:
                    raise GeminiTimeoutError() from exc
            elif not any(
                token in message
                for token in ("429", "404", "503", "unavailable", "not_found", "resource_exhausted")
            ):
                break

            if index < len(models) - 1:
                time.sleep(0.5)

    raise GeminiUnavailableError() from last_error


def identify_food(images) -> FoodIdentification:
    contents = [VISION_PROMPT]
    for index, image in enumerate(images, start=1):
        image.seek(0)
        contents.append(f"Foto sudut ke-{index}: {image.name}")
        contents.append(
            types.Part.from_bytes(
                data=image.read(),
                mime_type=image.content_type,
            )
        )
        image.seek(0)

    result = _generate_json(contents)
    food_name = result.get("food_name")
    if isinstance(food_name, str):
        food_name = food_name.strip() or None
    elif food_name is not None:
        raise GeminiResponseError()

    confidence = str(result.get("confidence", "rendah")).lower()
    if confidence not in {"tinggi", "sedang", "rendah"}:
        confidence = "rendah"

    ingredients = result.get("ingredients", [])
    if not isinstance(ingredients, list):
        ingredients = []

    return FoodIdentification(
        food_name=food_name,
        confidence=confidence,
        ingredients=ingredients,
        notes=str(result.get("notes", "")).strip(),
    )

