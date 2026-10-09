from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient


def make_image(name="food.jpg", image_format="JPEG", size=(20, 20)):
    buffer = BytesIO()
    Image.new("RGB", size, color="orange").save(buffer, format=image_format)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


class HealthEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint(self):
        response = self.client.get(reverse("api:health"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])


class FoodAnalysisEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_images_are_required(self):
        response = self.client.post(reverse("api:analyze"), data={}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")

    @override_settings(GEMINI_API_KEY="")
    def test_missing_api_key_returns_safe_service_error(self):
        response = self.client.post(
            reverse("api:analyze"),
            data={"images": [make_image()]},
            format="multipart",
        )
        body = response.json()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(body["error"]["code"], "GEMINI_NOT_CONFIGURED")
        self.assertNotIn("API_KEY", body["error"]["message"])

    @override_settings(MAX_UPLOAD_IMAGES=2)
    def test_rejects_too_many_images(self):
        response = self.client.post(
            reverse("api:analyze"),
            data={"images": [make_image("one.jpg"), make_image("two.jpg"), make_image("three.jpg")]},
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)

    @patch("api.views.analyze_food_images")
    def test_returns_consistent_success_payload(self, analyze_mock):
        analyze_mock.return_value = {
            "identification": {
                "food_name": "Nasi Goreng",
                "identification_status": "IDENTIFIED",
                "confidence": "tinggi",
                "ingredients": [],
                "notes": "",
            },
            "matching": {
                "normalized_name": "nasi goreng",
                "status": "MATCHED",
                "duplicate_count": 1,
            },
            "nutrition": {
                "id": "773",
                "name": "Nasi Goreng",
                "calories": "276.0",
                "proteins": "3.2",
                "fat": "3.2",
                "carbohydrate": "30.2",
                "image": "",
            },
            "recommendation": "Berdasarkan data nutrisi dataset HealthCoach, pilih porsi sesuai kebutuhan.",
            "note": "Informasi umum.",
        }

        response = self.client.post(
            reverse("api:analyze"),
            data={"images": [make_image("front.jpg"), make_image("side.jpg")]},
            format="multipart",
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertEqual(body["meta"]["images_received"], 2)
        self.assertEqual(body["data"]["identification"]["food_name"], "Nasi Goreng")
        analyze_mock.assert_called_once()

    @patch("api.views.analyze_food_images")
    def test_legacy_single_image_field_is_supported(self, analyze_mock):
        analyze_mock.return_value = {
            "identification": {},
            "matching": {},
            "nutrition": None,
            "recommendation": "",
            "note": "",
        }
        response = self.client.post(
            reverse("api:analyze"),
            data={"image": make_image()},
            format="multipart",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["meta"]["images_received"], 1)

