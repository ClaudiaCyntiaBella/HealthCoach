"""Rekomendasi Gemini yang tidak boleh mengubah angka dari dataset."""

import json
import re

from api.exceptions import GeminiResponseError
from api.services.gemini import _generate_json
from api.services.nutrition import NutritionMatch


NUTRITION_UNAVAILABLE_RECOMMENDATION = (
    "Informasi nutrisi untuk makanan ini belum tersedia pada dataset HealthCoach, "
    "sehingga sistem belum dapat memberikan rekomendasi berdasarkan data nutrisi."
)
NUTRITION_UNAVAILABLE_NOTE = (
    "Makanan berhasil diidentifikasi, tetapi informasi nutrisinya belum tersedia "
    "pada dataset HealthCoach."
)
UNKNOWN_RECOMMENDATION = (
    "Makanan belum dapat diidentifikasi dengan yakin dari foto. Silakan unggah "
    "foto yang lebih terang dan jelas dari beberapa sudut."
)


def _build_prompt(match: NutritionMatch) -> str:
    official_input = {
        "food_name": match.identified_name,
        "identification_status": match.identification_status,
        "matching_status": match.matching_status,
        "nutrition": match.nutrition,
    }
    return f"""
Anda adalah asisten informasi nutrisi HealthCoach. Gunakan HANYA data resmi
sistem berikut. Jangan menghitung, mengubah, atau menebak nilai nutrisi.

DATA RESMI SISTEM:
{json.dumps(official_input, ensure_ascii=False, indent=2)}

Aturan:
1. Salin food_name, identification_status, matching_status, dan objek nutrition
   persis dari data resmi.
2. Recommendation harus Bahasa Indonesia, singkat, berupa informasi umum,
   bukan diagnosis atau pengganti tenaga kesehatan.
3. Recommendation wajib diawali "Berdasarkan data nutrisi dataset HealthCoach,".
4. Jangan tulis angka pada recommendation atau note. Angka hanya boleh berada
   di objek nutrition.
5. Kembalikan JSON valid saja dengan kunci: food_name,
   identification_status, matching_status, nutrition, recommendation, note.
""".strip()


def _fallback_recommendation(match: NutritionMatch) -> dict:
    if match.identification_status == "UNKNOWN":
        return {
            "recommendation": UNKNOWN_RECOMMENDATION,
            "note": "Sistem tidak memberikan informasi nutrisi untuk hasil UNKNOWN.",
        }
    return {
        "recommendation": NUTRITION_UNAVAILABLE_RECOMMENDATION,
        "note": NUTRITION_UNAVAILABLE_NOTE,
    }


def _validate(match: NutritionMatch, result: dict) -> None:
    expected = {
        "food_name": match.identified_name,
        "identification_status": match.identification_status,
        "matching_status": match.matching_status,
        "nutrition": match.nutrition,
    }
    if any(result.get(key) != value for key, value in expected.items()):
        raise GeminiResponseError()
    if not str(result.get("recommendation", "")).startswith(
        "Berdasarkan data nutrisi dataset HealthCoach,"
    ):
        raise GeminiResponseError()
    if re.search(r"\d", f"{result.get('recommendation', '')} {result.get('note', '')}"):
        raise GeminiResponseError()


def generate_recommendation(match: NutritionMatch) -> dict:
    if match.matching_status != "MATCHED":
        return _fallback_recommendation(match)

    result = _generate_json(_build_prompt(match))
    _validate(match, result)
    return {
        "recommendation": result["recommendation"],
        "note": str(result.get("note", "")),
    }

