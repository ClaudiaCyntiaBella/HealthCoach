
"""Pengujian penyimpanan hasil analisis ke riwayat pengguna."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.exceptions import GeminiResponseError
from api.models import FoodAnalysisHistory
from api.tests.test_api import make_image


User = get_user_model()


class FoodAnalysisHistorySaveTests(TestCase):
    """Menguji penyimpanan hasil analisis melalui endpoint Django."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="tiwi_history_test",
            password="password-khusus-testing",
        )
        self.url = reverse("api:analyze")

        # Contoh hasil pipeline untuk pengujian API.
        self.analysis_result = {
            "identification": {
                "food_name": "Nasi Goreng",
                "identification_status": "IDENTIFIED",
            },
            "matching": {
                "status": "MATCHED",
                "method": "EXACT",
            },
            "nutrition": {
                "calories": "276",
                "proteins": "3.2",
                "carbohydrate": "30.2",
                "fat": "3.2",
            },
            "nutrition_source": "DATASET",
            "estimation_note": None,
            "recommendation": "Tambahkan sayuran.",
            "recommendation_details": {},
            "note": "Data berasal dari dataset.",
        }

    def authenticate_user(self):
        # Menggunakan access token JWT untuk request.
        token = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token.access_token}"
        )

    @patch("api.views.analyze_food_images")
    def test_authenticated_analysis_is_saved(self, analyze_mock):
        """Analisis pengguna login harus disimpan ke riwayat."""

        self.authenticate_user()
        analyze_mock.return_value = self.analysis_result

        response = self.client.post(
            self.url,
            data={"images": [make_image()]},
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])

        # Hasil analisis tetap dikembalikan melalui API.
        self.assertEqual(
            body["data"],
            self.analysis_result,
        )

        # Pastikan riwayat benar-benar tersimpan.
        self.assertEqual(
            FoodAnalysisHistory.objects.count(),
            1,
        )

        history = FoodAnalysisHistory.objects.get()

        self.assertEqual(history.user, self.user)
        self.assertEqual(
            history.result,
            self.analysis_result,
        )
        self.assertEqual(
            body["meta"]["history_id"],
            history.id,
        )

        analyze_mock.assert_called_once()

    @patch("api.views.analyze_food_images")
    def test_anonymous_analysis_is_not_saved(self, analyze_mock):
        """Analisis anonim tetap berjalan, tetapi tidak disimpan."""

        analyze_mock.return_value = self.analysis_result

        response = self.client.post(
            self.url,
            data={"images": [make_image()]},
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])

        self.assertIsNone(
            body["meta"]["history_id"]
        )

        self.assertFalse(
            FoodAnalysisHistory.objects.exists()
        )

        analyze_mock.assert_called_once()

    @patch(
        "api.views.analyze_food_images",
        side_effect=GeminiResponseError(),
    )
    def test_failed_analysis_is_not_saved(self, analyze_mock):
        """Analisis gagal tidak boleh menghasilkan riwayat."""

        self.authenticate_user()

        response = self.client.post(
            self.url,
            data={"images": [make_image()]},
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 502)
        self.assertFalse(body["success"])

        self.assertEqual(
            body["error"]["code"],
            "GEMINI_INVALID_RESPONSE",
        )

        self.assertFalse(
            FoodAnalysisHistory.objects.exists()
        )

        analyze_mock.assert_called_once()

    @patch("api.views.analyze_food_images")
    def test_non_food_result_is_not_saved(self, analyze_mock):
        """Validasi NON_FOOD yang sukses secara API tidak boleh masuk riwayat."""
        self.authenticate_user()
        rejected_result = {
            **self.analysis_result,
            "identification": {
                "food_name": None,
                "identification_status": "UNKNOWN",
                "image_category": "NON_FOOD",
            },
            "matching": {"status": "NOT_MATCHED", "method": "NONE"},
            "nutrition": None,
            "nutrition_source": "UNAVAILABLE",
        }
        analyze_mock.return_value = rejected_result

        response = self.client.post(
            self.url, data={"images": [make_image()]}, format="multipart"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["meta"]["history_id"])
        self.assertFalse(FoodAnalysisHistory.objects.exists())

    @patch("api.views.analyze_food_images")
    def test_too_blurry_result_is_not_saved(self, analyze_mock):
        self.authenticate_user()
        analyze_mock.return_value = {
            **self.analysis_result,
            "identification": {
                "food_name": None,
                "identification_status": "UNKNOWN",
                "image_category": "UNCERTAIN",
                "image_quality": "TOO_BLURRY",
            },
            "matching": {"status": "NOT_MATCHED", "method": "NONE"},
            "nutrition": None,
            "nutrition_source": "UNAVAILABLE",
        }

        response = self.client.post(
            self.url, data={"images": [make_image()]}, format="multipart"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["meta"]["history_id"])
        self.assertFalse(FoodAnalysisHistory.objects.exists())
