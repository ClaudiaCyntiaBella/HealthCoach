
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

PHOTO_SLOT_NAMES = ("Tampak Atas", "Sudut Samping", "Detail Makanan")

MULTI_PHOTO_VALIDATION_PROMPT = """
Anda adalah validator konsistensi foto untuk HealthCoach. Foto yang diberikan
berurutan dalam slot Tampak Atas, Sudut Samping, dan Detail Makanan.

Nilai SETIAP foto secara terpisah. Jangan mengabaikan foto yang bukan makanan
hanya karena foto lain berisi makanan. Foto dapat diterima bila seluruh foto
menampilkan satu hidangan/porsi yang sama atau komponen yang jelas terkait
(misalnya nasi, ayam, sayur, dan sambal dalam satu porsi).

Tolak set jika salah satu foto NON_FOOD, TOO_BLURRY, UNCERTAIN, atau bila dua
foto menampilkan makanan/minuman yang tidak terkait. Keyboard, manusia, gelas
kosong, kemasan kosong, dokumen, dan benda lain adalah NON_FOOD. Jangan
menganggap objek buram sebagai makanan.

Kembalikan JSON valid saja:
{
  "relationship_status": "CONSISTENT | INCONSISTENT",
  "notes": "alasan singkat",
  "slots": [
    {
      "slot_number": 1,
      "image_category": "FOOD | BEVERAGE | NON_FOOD | UNCERTAIN",
      "image_quality": "CLEAR | MODERATELY_BLURRY | TOO_BLURRY",
      "related_to_same_dish": true,
      "reason": "alasan singkat"
    }
  ]
}
""".strip()

VISION_PROMPT = """
Anda adalah sistem identifikasi makanan untuk aplikasi HealthCoach.

Semua foto yang diberikan merupakan beberapa sudut dari SATU makanan atau satu
porsi yang sama. Gabungkan informasi dari seluruh foto untuk membuat satu hasil.
Jangan mengarang nilai nutrisi, diagnosis, atau rekomendasi diet.

Tugas:
1. Klasifikasikan konteks utama foto menjadi FOOD, BEVERAGE, NON_FOOD, atau
   UNCERTAIN. Foto hanya FOOD/BEVERAGE bila makanan/minuman nyata menjadi objek
   utama; kemasan, gambar, dokumen, layar, atau benda berbentuk makanan bukan
   bukti makanan/minuman nyata.
2. Nilai kualitas visual gabungan foto menjadi CLEAR, MODERATELY_BLURRY, atau
   TOO_BLURRY dengan mempertimbangkan blur, ketajaman, pencahayaan, dan
   keterbacaan objek. Gunakan TOO_BLURRY jika makanan tidak dapat dikenali
   dengan andal; pada kondisi ini food_name dan canonical_food_name wajib null.
3. Hanya jika kategori FOOD/BEVERAGE dan kualitas bukan TOO_BLURRY, tentukan
   nama makanan utama dalam Bahasa Indonesia.
4. Tentukan nama makanan dasar bila makanan merupakan variasi dari makanan
   utama. Contoh: untuk "nasi goreng ayam", food_name adalah "Nasi goreng ayam"
   dan canonical_food_name adalah "Nasi Goreng". Gunakan null jika tidak yakin;
   jangan menebak nama makanan dasar.
5. Catat komponen yang benar-benar terlihat dan yang hanya diperkirakan.
6. Berikan keyakinan: tinggi, sedang, atau rendah.
7. Jika kategori NON_FOOD atau UNCERTAIN, food_name dan canonical_food_name wajib
   null dan jelaskan alasannya pada notes.

Kembalikan JSON valid saja:
{
  "image_category": "FOOD | BEVERAGE | NON_FOOD | UNCERTAIN",
  "image_quality": "CLEAR | MODERATELY_BLURRY | TOO_BLURRY",
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
    image_category: str = "FOOD"
    image_quality: str = "CLEAR"

    @property
    def status(self) -> str:
        return (
            "IDENTIFIED"
            if (
                self.image_category in {"FOOD", "BEVERAGE"}
                and self.image_quality != "TOO_BLURRY"
                and self.food_name
            )
            else "UNKNOWN"
        )

    @property
    def is_analyzable(self) -> bool:
        return self.image_category in {"FOOD", "BEVERAGE"} and self.status == "IDENTIFIED"

    def to_dict(self) -> dict:
        return {
            "food_name": self.food_name,
            "canonical_food_name": self.canonical_food_name,
            "image_category": self.image_category,
            "image_quality": self.image_quality,
            "identification_status": self.status,
            "confidence": self.confidence,
            "ingredients": self.ingredients,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class PhotoSlotValidation:
    slot_number: int
    slot_name: str
    image_category: str
    image_quality: str
    related_to_same_dish: bool
    reason: str

    def to_dict(self) -> dict:
        return {
            "slot_number": self.slot_number,
            "slot_name": self.slot_name,
            "image_category": self.image_category,
            "image_quality": self.image_quality,
            "related_to_same_dish": self.related_to_same_dish,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class MultiPhotoValidation:
    status: str
    message: str
    slots: list[PhotoSlotValidation]
    invalid_slots: list[PhotoSlotValidation]
    notes: str

    @property
    def is_valid(self) -> bool:
        return self.status == "VALID"

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "message": self.message,
            "notes": self.notes,
            "invalid_slots": [slot.to_dict() for slot in self.invalid_slots],
            "slots": [slot.to_dict() for slot in self.slots],
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

    image_category = result.get("image_category")
    if image_category not in {"FOOD", "BEVERAGE", "NON_FOOD", "UNCERTAIN"}:
        raise GeminiResponseError()

    image_quality = result.get("image_quality")
    if image_quality not in {"CLEAR", "MODERATELY_BLURRY", "TOO_BLURRY"}:
        raise GeminiResponseError()

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
    if (image_category in {"NON_FOOD", "UNCERTAIN"} or image_quality == "TOO_BLURRY") and (
        food_name is not None or canonical_food_name is not None
    ):
        raise GeminiResponseError()
    if (
        image_category in {"FOOD", "BEVERAGE"}
        and image_quality != "TOO_BLURRY"
        and food_name is None
    ):
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
        image_category=image_category,
        image_quality=image_quality,
    )


def _slot_name(slot_number: int) -> str:
    return PHOTO_SLOT_NAMES[slot_number - 1]


def _validation_message(invalid_slots: list[PhotoSlotValidation]) -> str:
    first_slot = invalid_slots[0]
    if first_slot.image_category == "NON_FOOD":
        return (
            f"Foto pada slot {first_slot.slot_name} bukan merupakan foto makanan "
            "atau minuman. Silakan unggah foto yang sesuai."
        )
    if first_slot.image_quality == "TOO_BLURRY":
        return (
            f"Foto pada slot {first_slot.slot_name} terlalu buram. "
            "Silakan unggah foto yang lebih jelas."
        )
    if first_slot.image_category == "UNCERTAIN":
        return (
            f"Foto pada slot {first_slot.slot_name} tidak dapat dikenali dengan jelas. "
            "Silakan unggah foto makanan atau minuman yang lebih jelas."
        )
    return (
        "Beberapa foto yang diunggah tidak menunjukkan makanan atau porsi yang sama. "
        "Silakan ganti foto yang tidak sesuai."
    )


def validate_image_set(images) -> MultiPhotoValidation:
    """Validasi tiap foto dan konsistensinya sebelum identifikasi hidangan."""
    if not 1 <= len(images) <= len(PHOTO_SLOT_NAMES):
        raise GeminiResponseError()

    contents = [MULTI_PHOTO_VALIDATION_PROMPT]
    for index, image in enumerate(images, start=1):
        image.seek(0)
        contents.append(f"Slot {index} ({_slot_name(index)}): {image.name}")
        contents.append(
            types.Part.from_bytes(data=image.read(), mime_type=image.content_type)
        )
        image.seek(0)

    result = _generate_json(contents)
    relationship_status = result.get("relationship_status")
    slots_value = result.get("slots")
    notes = result.get("notes", "")
    if (
        relationship_status not in {"CONSISTENT", "INCONSISTENT"}
        or not isinstance(slots_value, list)
        or len(slots_value) != len(images)
        or not isinstance(notes, str)
    ):
        raise GeminiResponseError()

    slots = []
    seen_slot_numbers = set()
    for raw_slot in slots_value:
        if not isinstance(raw_slot, dict):
            raise GeminiResponseError()
        slot_number = raw_slot.get("slot_number")
        category = raw_slot.get("image_category")
        quality = raw_slot.get("image_quality")
        related = raw_slot.get("related_to_same_dish")
        reason = raw_slot.get("reason")
        if (
            not isinstance(slot_number, int)
            or slot_number not in range(1, len(images) + 1)
            or slot_number in seen_slot_numbers
            or category not in {"FOOD", "BEVERAGE", "NON_FOOD", "UNCERTAIN"}
            or quality not in {"CLEAR", "MODERATELY_BLURRY", "TOO_BLURRY"}
            or not isinstance(related, bool)
            or not isinstance(reason, str)
        ):
            raise GeminiResponseError()
        seen_slot_numbers.add(slot_number)
        slots.append(
            PhotoSlotValidation(
                slot_number=slot_number,
                slot_name=_slot_name(slot_number),
                image_category=category,
                image_quality=quality,
                related_to_same_dish=related,
                reason=reason.strip(),
            )
        )

    slots.sort(key=lambda slot: slot.slot_number)
    invalid_slots = [
        slot for slot in slots
        if slot.image_category in {"NON_FOOD", "UNCERTAIN"}
        or slot.image_quality == "TOO_BLURRY"
    ]
    if len(images) > 1 and (
        relationship_status == "INCONSISTENT"
        or any(not slot.related_to_same_dish for slot in slots)
    ):
        invalid_slots.extend(
            slot for slot in slots
            if not slot.related_to_same_dish and slot not in invalid_slots
        )
        if not invalid_slots:
            invalid_slots.append(slots[0])

    if invalid_slots:
        return MultiPhotoValidation(
            status="REJECTED",
            message=_validation_message(invalid_slots),
            slots=slots,
            invalid_slots=invalid_slots,
            notes=notes.strip(),
        )

    return MultiPhotoValidation(
        status="VALID",
        message="Semua foto valid dan menunjukkan satu makanan atau porsi yang sama.",
        slots=slots,
        invalid_slots=[],
        notes=notes.strip(),
    )
