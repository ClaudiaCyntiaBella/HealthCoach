
"""Integrasi Gemini Vision untuk identifikasi makanan dari beberapa sudut."""

import json
import logging
import time
from dataclasses import dataclass

from django.conf import settings
from google import genai
from google.genai import types

from api.exceptions import (
    GeminiAuthenticationError,
    GeminiConfigurationError,
    GeminiQuotaError,
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
2. Tentukan nama makanan dasar bila makanan merupakan variasi dari makanan
   utama. Contoh: untuk "nasi goreng ayam", food_name adalah "Nasi goreng ayam"
   dan canonical_food_name adalah "Nasi Goreng". Gunakan null jika tidak yakin;
   jangan menebak nama makanan dasar.
3. Catat komponen yang benar-benar terlihat dan yang hanya diperkirakan.
4. Berikan keyakinan: tinggi, sedang, atau rendah.
5. Jika objek bukan makanan atau tidak cukup jelas, gunakan food_name null dan
   jelaskan alasannya pada notes.

Kembalikan JSON valid saja:
{
  "food_name": "nama makanan atau null",
  "canonical_food_name": "nama makanan dasar atau null",
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
    canonical_food_name: str | None
    confidence: str
    ingredients: list[dict]
    notes: str

    @property
    def status(self) -> str:
        return "IDENTIFIED" if self.food_name else "UNKNOWN"

    def to_dict(self) -> dict:
        return {
            "food_name": self.food_name,
            "canonical_food_name": self.canonical_food_name,
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
        http_options=types.HttpOptions(
            timeout=settings.GEMINI_TIMEOUT_SECONDS * 1000
        ),
    )


def _classify_error(exc: Exception):
    """Kembalikan kategori kesalahan tanpa membocorkan detail provider."""
    message = str(exc).lower()
    error_type = type(exc).__name__.lower()
    status_code = getattr(exc, "code", None)

    if status_code == 429 or any(
        token in message for token in ("429", "resource_exhausted", "quota")
    ):
        return GeminiQuotaError
    if status_code == 400 or any(
        token in message for token in ("invalid api key", "api key not valid", "400")
    ):
        return GeminiConfigurationError
    if status_code in {401, 403} or any(
        token in message for token in ("401", "403", "permission_denied", "unauthenticated")
    ):
        return GeminiAuthenticationError
    if "timeout" in message or "deadline" in message or "timeout" in error_type:
        return GeminiTimeoutError
    return GeminiUnavailableError


def _is_temporary_error(exc: Exception) -> bool:
    if getattr(exc, "code", None) in {500, 502, 503, 504}:
        return True
    message = str(exc).lower()
    return any(
        token in message
        for token in ("500", "502", "503", "504", "unavailable", "servererror")
    )


def _generate_json(contents) -> dict:
    client = _create_client()

    models = tuple(
        dict.fromkeys(
            model
            for model in (
                settings.GEMINI_MODEL,
                settings.GEMINI_FALLBACK_MODEL,
            )
            if model
        )
    )

    if not models:
        raise GeminiConfigurationError()

    last_error = None

    for model in models:
        for attempt in range(settings.GEMINI_MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                        automatic_function_calling=(
                            types.AutomaticFunctionCallingConfig(disable=True)
                        ),
                    ),
                )
                return _parse_json_response(response.text)
            except GeminiResponseError:
                raise
            except Exception as exc:
                last_error = exc
                error_class = _classify_error(exc)
                logger.warning(
                    "Gemini gagal: model=%s attempt=%d type=%s http_status=%s provider_status=%s",
                    model,
                    attempt + 1,
                    type(exc).__name__,
                    getattr(exc, "code", None),
                    getattr(exc, "status", None),
                )
                # Kesalahan konfigurasi, akses, kuota, dan timeout tidak diulang.
                if error_class is not GeminiUnavailableError:
                    raise error_class() from exc
                if _is_temporary_error(exc) and attempt < settings.GEMINI_MAX_RETRIES:
                    time.sleep(settings.GEMINI_RETRY_DELAY_SECONDS)
                    continue
                break

    if last_error is not None:
        raise GeminiUnavailableError() from last_error

    raise GeminiUnavailableError()


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

    def optional_food_name(key: str) -> str | None:
        if key not in result:
            raise GeminiResponseError()
        value = result.get(key)
        if isinstance(value, str):
            return value.strip() or None
        if value is None:
            return None
        raise GeminiResponseError()

    food_name = optional_food_name("food_name")
    canonical_food_name = optional_food_name("canonical_food_name")

    # Canonical name tanpa nama makanan utama adalah respons yang tidak konsisten.
    # Menolaknya mencegah hasil UNKNOWN memperoleh data nutrisi melalui canonical match.
    if food_name is None and canonical_food_name is not None:
        raise GeminiResponseError()

    raw_confidence = result.get("confidence", "rendah")
    if not isinstance(raw_confidence, str):
        raise GeminiResponseError()
    confidence = raw_confidence.lower()

    if confidence not in {"tinggi", "sedang", "rendah"}:
        confidence = "rendah"

    ingredients = result.get("ingredients", [])
    if not isinstance(ingredients, list):
        raise GeminiResponseError()
    for ingredient in ingredients:
        if not isinstance(ingredient, dict):
            raise GeminiResponseError()
        if not isinstance(ingredient.get("name"), str):
            raise GeminiResponseError()
        if not isinstance(ingredient.get("visible"), bool):
            raise GeminiResponseError()
        if ingredient.get("confidence") not in {"tinggi", "sedang", "rendah"}:
            raise GeminiResponseError()

    notes = result.get("notes", "")
    if not isinstance(notes, str):
        raise GeminiResponseError()

    return FoodIdentification(
        food_name=food_name,
        canonical_food_name=canonical_food_name,
        confidence=confidence,
        ingredients=ingredients,
        notes=notes.strip(),
    )
