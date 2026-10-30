
import csv
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from api.exceptions import (
    GeminiAuthenticationError,
    GeminiConfigurationError,
    GeminiQuotaError,
    GeminiResponseError,
    GeminiTimeoutError,
)
from api.models import Nutrition
from api.services.gemini import (
    FoodIdentification,
    _classify_error,
    _parse_json_response,
    identify_food,
)
from api.services.pipeline import analyze_food_images
from api.services.nutrition import (
    CsvNutritionRepository,
    DjangoNutritionRepository,
    NutritionMatch,
    normalize_food_name,
)
from api.services.recommendation import generate_recommendation


class NutritionRepositoryTests(SimpleTestCase):
    def setUp(self):
        temporary = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            newline="",
            encoding="utf-8",
        )
        self.addCleanup(
            lambda: Path(temporary.name).unlink(missing_ok=True)
        )

        writer = csv.DictWriter(
            temporary,
            fieldnames=[
                "id",
                "calories",
                "proteins",
                "fat",
                "carbohydrate",
                "name",
                "image",
                "name_normalized",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "id": "1",
                "calories": "276.0",
                "proteins": "3.2",
                "fat": "3.2",
                "carbohydrate": "30.2",
                "name": "Nasi Goreng",
                "image": "",
                "name_normalized": "nasi goreng",
            }
        )
        temporary.close()

        self.repository = CsvNutritionRepository(
            Path(temporary.name)
        )

    def test_normalization_matches_dataset_rule(self):
        self.assertEqual(
            normalize_food_name("  NASI   Goreng! "),
            "nasi goreng",
        )

    def test_exact_match(self):
        result = self.repository.find_exact("nASI gorEng")

        self.assertEqual(result.matching_status, "MATCHED")
        self.assertEqual(
            result.nutrition["calories"],
            "276.0",
        )

    def test_not_matched_does_not_invent_nutrition(self):
        result = self.repository.find_exact("Pizza")

        self.assertEqual(
            result.matching_status,
            "NOT_MATCHED",
        )
        self.assertIsNone(result.nutrition)

    def test_canonical_name_matches_a_dataset_reference(self):
        result = self.repository.find_for_identification(
            "Nasi goreng ayam",
            "Nasi Goreng",
        )

        self.assertEqual(result.matching_status, "MATCHED")
        self.assertEqual(result.match_method, "CANONICAL")
        self.assertEqual(result.identified_name, "Nasi goreng ayam")
        self.assertEqual(result.reference_name, "Nasi Goreng")
        self.assertEqual(result.nutrition["name"], "Nasi Goreng")


class DjangoNutritionRepositoryTests(TestCase):
    def setUp(self):
        Nutrition.objects.create(
            id=1,
            calories=212.0,
            proteins=18.0,
            fat=10.0,
            carbohydrate=12.0,
            name="Abon",
            image="",
            name_normalized="abon",
        )

        self.repository = DjangoNutritionRepository(
            "api.Nutrition"
        )

    def test_exact_match_returns_database_nutrition(self):
        result = self.repository.find_exact(" ABON! ")

        self.assertEqual(
            result.identification_status,
            "IDENTIFIED",
        )
        self.assertEqual(
            result.matching_status,
            "MATCHED",
        )
        self.assertEqual(result.normalized_name, "abon")
        self.assertEqual(result.duplicate_count, 1)
        self.assertEqual(
            result.nutrition["name"],
            "Abon",
        )
        self.assertEqual(
            result.nutrition["calories"],
            "212.0",
        )

    def test_not_matched_returns_empty_nutrition(self):
        result = self.repository.find_exact(
            "Makanan Tidak Ada"
        )

        self.assertEqual(
            result.matching_status,
            "NOT_MATCHED",
        )
        self.assertEqual(result.duplicate_count, 0)
        self.assertIsNone(result.nutrition)


class GeminiResponseParserTests(SimpleTestCase):
    def test_accepts_json_markdown_fence(self):
        result = _parse_json_response(
            '```json\n{"food_name": "Soto"}\n```'
        )

        self.assertEqual(result["food_name"], "Soto")

    def test_rejects_invalid_json(self):
        with self.assertRaises(GeminiResponseError):
            _parse_json_response("bukan json")

    def test_classifies_provider_errors_safely(self):
        self.assertIs(_classify_error(Exception("429 RESOURCE_EXHAUSTED")), GeminiQuotaError)
        self.assertIs(_classify_error(Exception("400 API key not valid")), GeminiConfigurationError)
        self.assertIs(_classify_error(TimeoutError("request timeout")), GeminiTimeoutError)

    def test_classifies_provider_http_statuses_without_exposing_key(self):
        error = Exception("provider failure")
        error.code = 403
        self.assertIs(_classify_error(error), GeminiAuthenticationError)

        error.code = 503
        self.assertNotEqual(_classify_error(error), GeminiConfigurationError)


class FoodIdentificationTests(SimpleTestCase):
    def _image(self, name):
        return SimpleUploadedFile(name, b"image-bytes", content_type="image/jpeg")

    @patch("api.services.gemini._generate_json")
    def test_uses_all_photos_as_one_food_context(self, generate_mock):
        generate_mock.return_value = {
            "food_name": "Nasi Goreng Ayam",
            "canonical_food_name": "Nasi Goreng",
            "confidence": "tinggi",
            "ingredients": [],
            "notes": "Nasi dan ayam terlihat.",
        }

        result = identify_food([self._image("front.jpg"), self._image("side.jpg")])

        self.assertEqual(result.food_name, "Nasi Goreng Ayam")
        self.assertEqual(result.canonical_food_name, "Nasi Goreng")
        contents = generate_mock.call_args.args[0]
        self.assertIn("Foto sudut ke-1: front.jpg", contents)
        self.assertIn("Foto sudut ke-2: side.jpg", contents)

    @patch("api.services.gemini._generate_json")
    def test_accepts_distinct_food_names_without_forcing_canonical_name(self, generate_mock):
        for food_name in ("Nasi Goreng", "Bakso", "Soto Ayam", "Bayam Tumis"):
            generate_mock.return_value = {
                "food_name": food_name,
                "canonical_food_name": None,
                "confidence": "sedang",
                "ingredients": [],
                "notes": "Terlihat cukup jelas.",
            }
            result = identify_food([self._image("food.jpg")])
            self.assertEqual(result.food_name, food_name)
            self.assertIsNone(result.canonical_food_name)

    @patch("api.services.gemini._generate_json")
    def test_unknown_food_cannot_have_canonical_name(self, generate_mock):
        generate_mock.return_value = {
            "food_name": None,
            "canonical_food_name": "Nasi Goreng",
            "confidence": "rendah",
            "ingredients": [],
            "notes": "Foto tidak cukup jelas.",
        }

        with self.assertRaises(GeminiResponseError):
            identify_food([self._image("unclear.jpg")])

    @patch("api.services.gemini._generate_json")
    def test_non_food_or_unclear_image_returns_unknown(self, generate_mock):
        generate_mock.return_value = {
            "food_name": None,
            "canonical_food_name": None,
            "confidence": "rendah",
            "ingredients": [],
            "notes": "Objek bukan makanan atau tidak cukup jelas.",
        }

        result = identify_food([self._image("object.jpg")])
        self.assertEqual(result.status, "UNKNOWN")


class RecommendationTests(SimpleTestCase):
    @patch(
        "api.services.recommendation._generate_json"
    )
    def test_unmatched_result_does_not_call_gemini_or_invent_values(
        self,
        generate_mock,
    ):
        match = NutritionMatch(
            identified_name="Pizza",
            normalized_name="pizza",
            identification_status="IDENTIFIED",
            matching_status="NOT_MATCHED",
            nutrition=None,
        )

        result = generate_recommendation(match)

        self.assertIn(
            "belum tersedia",
            result["recommendation"],
        )
        generate_mock.assert_not_called()

    @patch(
        "api.services.recommendation._generate_json"
    )
    def test_unknown_food_returns_clear_message(
        self,
        generate_mock,
    ):
        match = NutritionMatch(
            identified_name=None,
            normalized_name=None,
            identification_status="UNKNOWN",
            matching_status="NOT_MATCHED",
            nutrition=None,
        )

        result = generate_recommendation(match)

        self.assertIn(
            "Objek pada foto belum dapat dikenali",
            result["recommendation"],
        )
        self.assertIn(
            "silakan coba kembali",
            result["recommendation"],
        )
        generate_mock.assert_not_called()

    @patch(
        "api.services.recommendation._generate_json"
    )
    def test_matched_result_preserves_official_nutrition(
        self,
        generate_mock,
    ):
        nutrition = {
            "id": "1",
            "name": "Abon",
            "calories": "212.0",
            "proteins": "18.0",
            "fat": "10.0",
            "carbohydrate": "12.0",
            "image": "",
        }

        match = NutritionMatch(
            identified_name="Abon",
            normalized_name="abon",
            identification_status="IDENTIFIED",
            matching_status="MATCHED",
            nutrition=nutrition,
            duplicate_count=1,
        )

        generate_mock.return_value = {
            "food_name": "Abon",
            "identification_status": "IDENTIFIED",
            "matching_status": "MATCHED",
            "nutrition": nutrition,
            "recommendation": (
                "Berdasarkan data nutrisi dataset HealthCoach, "
                "makanan ini dapat menjadi bagian dari pola "
                "makan yang seimbang."
            ),
            "note": (
                "Sesuaikan konsumsi dengan kebutuhan pribadi."
            ),
            "recommendation_details": {
                "saran": "Padukan abon dengan sayuran dan sumber karbohidrat sesuai kebutuhan makan.",
                "alasan": "Protein merupakan salah satu zat gizi yang tercatat pada data abon.",
                "pendamping_alternatif": "Sayur bening dapat menjadi pendamping yang relevan.",
                "catatan_nutrisi": "Data nutrisi ditampilkan pada panel nutrisi HealthCoach.",
            },
        }

        result = generate_recommendation(match)

        generate_mock.assert_called_once()
        self.assertEqual(
            result["recommendation"],
            generate_mock.return_value["recommendation"],
        )
        self.assertEqual(
            generate_mock.return_value["nutrition"],
            nutrition,
        )
        self.assertIn("saran", result["details"])

    @patch("api.services.recommendation._generate_json")
    def test_contextual_recommendations_keep_each_food_context(self, generate_mock):
        cases = (
            ("Nasi Goreng", "sayuran", "Tambahkan sayuran sebagai pelengkap nasi goreng."),
            ("Bakso", "sawi", "Tambahkan sawi atau sayuran lain pada sajian bakso."),
            ("Soto Ayam", "kuah", "Pilih pelengkap yang sesuai dengan sajian soto berkuah."),
            ("Bayam Tumis", "protein", "Padukan bayam tumis dengan sumber protein."),
        )

        for food_name, expected_term, advice in cases:
            nutrition = {
                "id": "1", "name": food_name, "calories": "100.0",
                "proteins": "5.0", "fat": "3.0", "carbohydrate": "12.0", "image": "",
            }
            match = NutritionMatch(food_name, food_name.lower(), "IDENTIFIED", "MATCHED", nutrition)
            generate_mock.return_value = {
                "food_name": food_name,
                "identification_status": "IDENTIFIED",
                "matching_status": "MATCHED",
                "nutrition": nutrition,
                "recommendation": advice,
                "note": "Informasi umum.",
                "recommendation_details": {
                    "saran": advice,
                    "alasan": f"Saran disesuaikan dengan {food_name} dan data yang tersedia.",
                    "pendamping_alternatif": "Pilih pendamping yang relevan dengan hidangan.",
                    "catatan_nutrisi": "Gunakan panel nutrisi sebagai rujukan.",
                },
            }

            result = generate_recommendation(match)
            self.assertIn(expected_term, result["details"]["saran"].lower())
            self.assertEqual(result["details"], generate_mock.return_value["recommendation_details"])
            self.assertEqual(generate_mock.return_value["nutrition"], nutrition)

        self.assertEqual(generate_mock.call_count, len(cases))


class AnalysisPipelineTests(SimpleTestCase):
    @patch("api.services.pipeline.generate_recommendation")
    @patch("api.services.pipeline.get_nutrition_repository")
    @patch("api.services.pipeline.identify_food")
    def test_uses_canonical_name_for_dataset_matching(
        self,
        identify_mock,
        repository_mock,
        recommendation_mock,
    ):
        identify_mock.return_value = FoodIdentification(
            food_name="Nasi goreng ayam",
            canonical_food_name="Nasi Goreng",
            confidence="tinggi",
            ingredients=[],
            notes="Ayam terlihat pada nasi goreng.",
        )
        repository_mock.return_value.find_for_identification.return_value = NutritionMatch(
            identified_name="Nasi goreng ayam",
            normalized_name="nasi goreng",
            identification_status="IDENTIFIED",
            matching_status="MATCHED",
            nutrition={"name": "Nasi Goreng"},
            match_method="CANONICAL",
            reference_name="Nasi Goreng",
        )
        recommendation_mock.return_value = {
            "recommendation": "Rekomendasi aman.",
            "note": "Informasi umum.",
            "details": {
                "saran": "Saran.",
                "alasan": "Alasan.",
                "pendamping_alternatif": "Pendamping.",
                "catatan_nutrisi": "Catatan.",
            },
        }

        result = analyze_food_images([object()])

        repository_mock.return_value.find_for_identification.assert_called_once_with(
            "Nasi goreng ayam",
            "Nasi Goreng",
        )
        self.assertEqual(result["matching"]["method"], "CANONICAL")
        self.assertEqual(result["matching"]["reference_name"], "Nasi Goreng")
        self.assertIn("referensi Nasi Goreng", result["note"])
        self.assertIn("saran", result["recommendation_details"])
