"""Pengujian prompt Gemini untuk rekomendasi dari data nutrisi HealthCoach."""

import json
import os
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from google import genai
from google.genai import types


PROJECT_DIR = Path(__file__).resolve().parents[2]
TESTING_DIR = Path(__file__).resolve().parent

# Samakan sumber credential dengan test_gemini.py. File .env lokal testing
# diprioritaskan; .env project hanya menjadi fallback bila diperlukan.
load_dotenv(TESTING_DIR / ".env")
load_dotenv(PROJECT_DIR / ".env")

IDENTIFIED = "IDENTIFIED"
UNKNOWN = "UNKNOWN"
MATCHED = "MATCHED"
NOT_MATCHED = "NOT_MATCHED"

NUTRITION_UNAVAILABLE_RECOMMENDATION = (
    "Informasi nutrisi untuk makanan ini belum tersedia pada dataset "
    "HealthCoach, sehingga sistem belum dapat memberikan rekomendasi "
    "berdasarkan data nutrisi."
)
NUTRITION_UNAVAILABLE_NOTE = (
    "Makanan berhasil diidentifikasi, tetapi informasi nutrisinya belum "
    "tersedia pada dataset HealthCoach."
)


@dataclass(frozen=True)
class FoodRecommendationInput:
    """Data resmi yang nantinya diberikan backend setelah proses matching."""

    food_name: str
    identification_status: Literal["IDENTIFIED", "UNKNOWN"]
    matching_status: Literal["MATCHED", "NOT_MATCHED"]
    calories: str | None = None
    proteins: str | None = None
    fat: str | None = None
    carbohydrate: str | None = None

    def __post_init__(self) -> None:
        nutrients = (self.calories, self.proteins, self.fat, self.carbohydrate)
        if self.matching_status == MATCHED and any(value is None for value in nutrients):
            raise ValueError("MATCHED harus memiliki seluruh nilai nutrisi dari dataset.")
        if self.matching_status == NOT_MATCHED and any(value is not None for value in nutrients):
            raise ValueError("NOT_MATCHED tidak boleh memiliki nilai nutrisi.")


def build_recommendation_prompt(food: FoodRecommendationInput) -> str:
    """Buat prompt yang membatasi Gemini pada data nutrisi dari sistem."""
    official_input = json.dumps(asdict(food), ensure_ascii=False, indent=2)

    return f"""
Anda adalah asisten informasi nutrisi untuk aplikasi HealthCoach.

Gunakan HANYA data resmi dari sistem berikut sebagai sumber nama makanan,
status, dan nilai nutrisi. Jangan memakai pengetahuan umum, jangan mencari
sumber lain, dan jangan menghitung, mengubah, atau menebak nilai nutrisi.

DATA RESMI SISTEM:
{official_input}

Aturan wajib:
1. Salin food_name, identification_status, dan matching_status persis dari data resmi.
2. Jika matching_status adalah MATCHED, nutrition wajib berisi calories,
   proteins, fat, dan carbohydrate persis seperti data resmi, tanpa perubahan.
3. Jika matching_status adalah NOT_MATCHED, nutrition wajib bernilai null.
   Jangan membuat, menebak, atau menyebutkan angka nutrisi apa pun.
4. Jangan menulis angka nutrisi dalam recommendation atau note; angka hanya
   boleh muncul pada objek nutrition yang disalin dari data resmi.
5. Rekomendasi harus Bahasa Indonesia, bersifat informasi umum, singkat,
   dan bukan diagnosis medis atau pengganti saran tenaga kesehatan.
6. Untuk IDENTIFIED + MATCHED, recommendation wajib diawali dengan
   "Berdasarkan data nutrisi dataset HealthCoach," agar jelas bahwa saran
   hanya merujuk pada data resmi yang diberikan.
7. Untuk IDENTIFIED + NOT_MATCHED, jangan memberikan saran konsumsi, pola
   makan, keseimbangan makanan, alternatif makanan, atau rekomendasi apa pun.
   Gunakan recommendation PERSIS sebagai berikut:
   "{NUTRITION_UNAVAILABLE_RECOMMENDATION}"
   Gunakan note PERSIS sebagai berikut:
   "{NUTRITION_UNAVAILABLE_NOTE}"
8. Untuk UNKNOWN + NOT_MATCHED, jelaskan bahwa makanan belum dapat
   diidentifikasi dengan yakin dari foto.

Kembalikan JSON valid saja, tanpa markdown dan tanpa teks tambahan, dengan format:
{{
  "food_name": "string",
  "identification_status": "IDENTIFIED atau UNKNOWN",
  "matching_status": "MATCHED atau NOT_MATCHED",
  "nutrition": {{
    "calories": "string",
    "proteins": "string",
    "fat": "string",
    "carbohydrate": "string"
  }} atau null,
  "recommendation": "string tanpa angka nutrisi",
  "note": "string tanpa angka nutrisi"
}}
""".strip()


def generate_recommendation(food: FoodRecommendationInput) -> dict:
    """Kirim prompt recommendation ke Gemini dan parse JSON responsnya."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY belum ditemukan pada file .env.")

    client = genai.Client(api_key=api_key)
    models = tuple(
        dict.fromkeys(
            (
                os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
                os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash"),
            )
        )
    )
    prompt = build_recommendation_prompt(food)
    last_error: Exception | None = None

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                ),
            )
            return json.loads(response.text)
        except Exception as error:
            last_error = error
            error_message = str(error)
            if not any(code in error_message for code in ("503", "429", "404", "UNAVAILABLE", "NOT_FOUND")):
                break
            time.sleep(2)

    raise RuntimeError("Gemini recommendation gagal dibuat.") from last_error


def validate_recommendation(
    food: FoodRecommendationInput,
    recommendation: dict,
) -> None:
    """Pastikan Gemini tidak mengubah atau membuat data nutrisi."""
    expected_statuses = {
        "food_name": food.food_name,
        "identification_status": food.identification_status,
        "matching_status": food.matching_status,
    }
    for key, expected_value in expected_statuses.items():
        if recommendation.get(key) != expected_value:
            raise AssertionError(f"Nilai {key} Gemini tidak sama dengan data sistem.")

    if food.matching_status == MATCHED:
        expected_nutrition = {
            "calories": food.calories,
            "proteins": food.proteins,
            "fat": food.fat,
            "carbohydrate": food.carbohydrate,
        }
        if recommendation.get("nutrition") != expected_nutrition:
            raise AssertionError("Gemini mengubah nilai nutrisi dari dataset.")
        if not recommendation.get("recommendation", "").startswith(
            "Berdasarkan data nutrisi dataset HealthCoach,"
        ):
            raise AssertionError(
                "Rekomendasi MATCHED tidak menyatakan sumber data dataset."
            )
    elif recommendation.get("nutrition") is not None:
        raise AssertionError("Gemini membuat nutrisi untuk makanan NOT_MATCHED.")

    if (
        food.identification_status == IDENTIFIED
        and food.matching_status == NOT_MATCHED
    ):
        if recommendation.get("recommendation") != NUTRITION_UNAVAILABLE_RECOMMENDATION:
            raise AssertionError(
                "Gemini memberi rekomendasi selain pemberitahuan data nutrisi "
                "tidak tersedia."
            )
        if recommendation.get("note") != NUTRITION_UNAVAILABLE_NOTE:
            raise AssertionError("Catatan NOT_MATCHED Gemini tidak sesuai.")

    # Prompt melarang angka di teks bebas supaya seluruh angka nutrisi hanya
    # berada pada objek nutrition yang dapat divalidasi terhadap data sistem.
    free_text = f"{recommendation.get('recommendation', '')} {recommendation.get('note', '')}"
    if re.search(r"\d", free_text):
        raise AssertionError("Gemini menulis angka pada teks bebas rekomendasi.")


def print_recommendation(recommendation: dict) -> None:
    """Tampilkan output Gemini dalam format yang mudah dibaca."""
    print(f"Nama Makanan              : {recommendation['food_name']}")
    print(f"Status Identifikasi       : {recommendation['identification_status']}")
    print(f"Status Matching           : {recommendation['matching_status']}")

    nutrition = recommendation["nutrition"]
    if nutrition is None:
        print("Calories                  : -")
        print("Proteins                  : -")
        print("Fat                       : -")
        print("Carbohydrate              : -")
    else:
        print(f"Calories                  : {nutrition['calories']}")
        print(f"Proteins                  : {nutrition['proteins']}")
        print(f"Fat                       : {nutrition['fat']}")
        print(f"Carbohydrate              : {nutrition['carbohydrate']}")

    print(f"Rekomendasi               : {recommendation['recommendation']}")
    print(f"Catatan                   : {recommendation['note']}")


def run_test_cases() -> None:
    """Uji data MATCHED dan IDENTIFIED + NOT_MATCHED."""
    test_cases = (
        (
            "Makanan dengan data nutrisi dataset",
            FoodRecommendationInput(
                food_name="Nasi Goreng",
                identification_status=IDENTIFIED,
                matching_status=MATCHED,
                calories="276.0",
                proteins="3.2",
                fat="3.2",
                carbohydrate="30.2",
            ),
        ),
        (
            "Makanan tanpa data nutrisi dataset",
            FoodRecommendationInput(
                food_name="Pizza",
                identification_status=IDENTIFIED,
                matching_status=NOT_MATCHED,
            ),
        ),
    )

    print("=" * 60)
    print("TEST PROMPT REKOMENDASI NUTRISI")
    print("=" * 60)

    for label, food in test_cases:
        print("\n" + "-" * 60)
        print(f"Test Case                 : {label}")
        recommendation = generate_recommendation(food)
        validate_recommendation(food, recommendation)
        print_recommendation(recommendation)
        print("Validasi nutrisi          : LULUS")


if __name__ == "__main__":
    run_test_cases()
