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
    "Objek pada foto belum dapat dikenali sebagai makanan dengan yakin. "
    "Pastikan foto menampilkan makanan yang ingin dianalisis dengan jelas, "
    "lalu silakan coba kembali."
)


def _fallback_details(match: NutritionMatch) -> dict:
    if match.identification_status == "UNKNOWN":
        return {
            "saran": "Ambil ulang foto dengan makanan terlihat utuh dan pencahayaan cukup.",
            "alasan": "Sistem belum cukup yakin mengenali objek pada foto sebagai makanan.",
            "pendamping_alternatif": "Tidak tersedia sebelum makanan dapat diidentifikasi.",
            "catatan_nutrisi": "Tidak ada data nutrisi yang ditampilkan untuk hasil ini.",
        }
    return {
        "saran": "Periksa kembali nama makanan atau gunakan foto yang lebih jelas.",
        "alasan": "Makanan teridentifikasi, tetapi belum memiliki kecocokan pada dataset nutrisi HealthCoach.",
        "pendamping_alternatif": "Tidak diberikan karena tidak ada dasar data nutrisi yang tervalidasi.",
        "catatan_nutrisi": NUTRITION_UNAVAILABLE_NOTE,
    }


def _build_prompt(match: NutritionMatch, nutrition: dict, nutrition_source: str) -> str:
    official_input = {
        "food_name": match.identified_name,
        "identification_status": match.identification_status,
        "matching_status": match.matching_status,
        "nutrition": nutrition,
        "nutrition_source": nutrition_source,
    }
    return f"""
Anda adalah asisten informasi nutrisi HealthCoach. Gunakan HANYA konteks sistem
berikut. Jangan menghitung, mengubah, atau menebak nilai nutrisi.

KONTEKS SISTEM:
{json.dumps(official_input, ensure_ascii=False, indent=2)}

Aturan:
1. Salin food_name, identification_status, matching_status, dan objek nutrition
   persis dari konteks sistem. Jika nutrition_source AI_ESTIMATED, sebutkan bahwa
   rekomendasi bersifat estimasi AI dan bukan data resmi dataset.
2. Recommendation harus Bahasa Indonesia, singkat, berupa informasi umum,
   bukan diagnosis atau pengganti tenaga kesehatan.
3. Buat rekomendasi kontekstual untuk food_name ini, bukan template umum. Gunakan
   nama makanan dan perbandingan relatif antar nilai nutrition yang tersedia.
4. Jangan melarang konsumsi kecuali ada alasan yang langsung didukung data.
5. Jangan tulis angka pada teks rekomendasi. Angka hanya boleh berada
   di objek nutrition.
6. Kembalikan JSON valid saja dengan kunci: food_name, identification_status,
   matching_status, nutrition, recommendation, note, recommendation_details.
   recommendation_details harus berisi saran, alasan, pendamping_alternatif,
   catatan_nutrisi. Setiap nilai berupa teks Bahasa Indonesia yang praktis.
""".strip()


def _fallback_recommendation(match: NutritionMatch) -> dict:
    if match.identification_status == "UNKNOWN":
        return {
            "recommendation": UNKNOWN_RECOMMENDATION,
            "note": "Sistem tidak memberikan informasi nutrisi untuk hasil UNKNOWN.",
            "details": _fallback_details(match),
        }
    return {
        "recommendation": NUTRITION_UNAVAILABLE_RECOMMENDATION,
        "note": NUTRITION_UNAVAILABLE_NOTE,
        "details": _fallback_details(match),
    }


def _validate(match: NutritionMatch, nutrition: dict, result: dict) -> None:
    expected = {
        "food_name": match.identified_name,
        "identification_status": match.identification_status,
        "matching_status": match.matching_status,
        "nutrition": nutrition,
    }
    if any(result.get(key) != value for key, value in expected.items()):
        raise GeminiResponseError()
    details = result.get("recommendation_details")
    if not isinstance(details, dict) or set(details) != {
        "saran", "alasan", "pendamping_alternatif", "catatan_nutrisi"
    }:
        raise GeminiResponseError()
    free_text = " ".join(str(value).strip() for value in details.values())
    if not all(str(value).strip() for value in details.values()):
        raise GeminiResponseError()
    if re.search(r"\d", f"{result.get('recommendation', '')} {result.get('note', '')} {free_text}"):
        raise GeminiResponseError()


def generate_recommendation(
    match: NutritionMatch,
    nutrition: dict | None = None,
    nutrition_source: str = "DATASET",
) -> dict:
    if nutrition_source not in {"DATASET", "AI_ESTIMATED", "UNAVAILABLE"}:
        raise GeminiResponseError()
    if nutrition_source == "DATASET":
        nutrition = match.nutrition
    if nutrition is None:
        return _fallback_recommendation(match)

    result = _generate_json(_build_prompt(match, nutrition, nutrition_source))
    _validate(match, nutrition, result)
    note = str(result.get("note", ""))
    if nutrition_source == "AI_ESTIMATED":
        note = f"{note} Rekomendasi ini didasarkan pada estimasi AI, bukan data resmi dataset.".strip()
    return {
        "recommendation": result["recommendation"],
        "note": note,
        "details": result["recommendation_details"],
    }

