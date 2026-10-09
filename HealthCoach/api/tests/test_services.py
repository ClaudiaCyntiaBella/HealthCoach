import csv
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from api.exceptions import GeminiResponseError
from api.services.gemini import _parse_json_response
from api.services.nutrition import CsvNutritionRepository, NutritionMatch, normalize_food_name
from api.services.recommendation import generate_recommendation


class NutritionRepositoryTests(SimpleTestCase):
    def setUp(self):
        temporary = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8")
        self.addCleanup(lambda: Path(temporary.name).unlink(missing_ok=True))
        writer = csv.DictWriter(
            temporary,
            fieldnames=["id", "calories", "proteins", "fat", "carbohydrate", "name", "image", "name_normalized"],
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
        self.repository = CsvNutritionRepository(Path(temporary.name))

    def test_normalization_matches_dataset_rule(self):
        self.assertEqual(normalize_food_name("  NASI   Goreng! "), "nasi goreng")

    def test_exact_match(self):
        result = self.repository.find_exact("nASI gorEng")
        self.assertEqual(result.matching_status, "MATCHED")
        self.assertEqual(result.nutrition["calories"], "276.0")

    def test_not_matched_does_not_invent_nutrition(self):
        result = self.repository.find_exact("Pizza")
        self.assertEqual(result.matching_status, "NOT_MATCHED")
        self.assertIsNone(result.nutrition)


class GeminiResponseParserTests(SimpleTestCase):
    def test_accepts_json_markdown_fence(self):
        result = _parse_json_response('```json\n{"food_name": "Soto"}\n```')
        self.assertEqual(result["food_name"], "Soto")

    def test_rejects_invalid_json(self):
        with self.assertRaises(GeminiResponseError):
            _parse_json_response("bukan json")


class RecommendationTests(SimpleTestCase):
    @patch("api.services.recommendation._generate_json")
    def test_unmatched_result_does_not_call_gemini_or_invent_values(self, generate_mock):
        match = NutritionMatch(
            identified_name="Pizza",
            normalized_name="pizza",
            identification_status="IDENTIFIED",
            matching_status="NOT_MATCHED",
            nutrition=None,
        )
        result = generate_recommendation(match)
        self.assertIn("belum tersedia", result["recommendation"])
        generate_mock.assert_not_called()

