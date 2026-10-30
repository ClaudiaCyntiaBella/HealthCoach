"""Estimasi nutrisi dari konteks visual Gemini untuk makanan tanpa dataset."""

import json
import math
from dataclasses import dataclass

from api.exceptions import GeminiResponseError
from api.services.gemini import FoodIdentification, _generate_json


AI_ESTIMATION_DISCLAIMER = (
    "Nilai nutrisi merupakan estimasi yang dihasilkan langsung oleh AI berdasarkan "
    "informasi visual dan identifikasi makanan. Nilai ini tidak berasal dari dataset "
    "atau referensi nutrisi eksternal. Hasil sebenarnya dapat berbeda berdasarkan "
    "porsi, bahan, dan proses pengolahan."
)


@dataclass(frozen=True)
class NutritionEstimation:
    nutrition: dict | None
    note: str

    @property
    def is_available(self) -> bool:
        return self.nutrition is not None


def _build_prompt(identification: FoodIdentification) -> str:
    visual_context = {
        "food_name": identification.food_name,
        "confidence": identification.confidence,
        "ingredients": identification.ingredients,
        "notes": identification.notes,
    }
    return f"""
Anda adalah pengestimasi nutrisi visual HealthCoach. Data berikut berasal dari
identifikasi visual satu porsi makanan dan BUKAN dari dataset atau database.

KONTEKS VISUAL:
{json.dumps(visual_context, ensure_ascii=False, indent=2)}

Aturan:
1. Buat estimasi hanya bila konteks visual cukup untuk memperkirakan satu porsi.
2. Pertimbangkan nama makanan, bahan yang terlihat, dan proses pengolahan yang
   benar-benar disebutkan pada konteks. Jangan memakai sumber nutrisi eksternal.
3. Estimasi bukan pengukuran pasti dan tidak boleh disebut data resmi atau laboratorium.
4. Jika porsi atau komposisi terlalu tidak pasti, gunakan estimate_available false
   dan nutrition null. Jangan mengarang angka.
5. Jika estimate_available true, semua nilai nutrition wajib berupa angka nol atau
   lebih besar: calories, proteins, carbohydrate, fat.
6. Kembalikan JSON valid saja:
{{
  "estimate_available": true,
  "nutrition": {{"calories": 0, "proteins": 0, "carbohydrate": 0, "fat": 0}} atau null,
  "estimation_note": "penjelasan singkat ketidakpastian estimasi"
}}
""".strip()


def _normalise_nutrition(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != {
        "calories", "proteins", "carbohydrate", "fat"
    }:
        raise GeminiResponseError()

    normalised = {}
    for key, number in value.items():
        if isinstance(number, bool) or not isinstance(number, (int, float)):
            raise GeminiResponseError()
        if not math.isfinite(number) or number < 0:
            raise GeminiResponseError()
        normalised[key] = f"{number:g}"
    return normalised


def estimate_nutrition(identification: FoodIdentification) -> NutritionEstimation:
    """Buat estimasi hanya untuk makanan teridentifikasi dengan visual cukup jelas."""
    if identification.status != "IDENTIFIED" or identification.confidence == "rendah":
        return NutritionEstimation(
            nutrition=None,
            note="Estimasi AI tidak tersedia karena identifikasi atau informasi visual belum cukup jelas.",
        )

    result = _generate_json(_build_prompt(identification))
    available = result.get("estimate_available")
    note = result.get("estimation_note")
    if not isinstance(available, bool) or not isinstance(note, str) or not note.strip():
        raise GeminiResponseError()

    if not available:
        if result.get("nutrition") is not None:
            raise GeminiResponseError()
        return NutritionEstimation(nutrition=None, note=note.strip())

    return NutritionEstimation(
        nutrition=_normalise_nutrition(result.get("nutrition")),
        note=note.strip(),
    )
