
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

from api.exceptions import (
    GeminiAuthenticationError,
    GeminiQuotaError,
    GeminiResponseError,
)


def make_image(name="food.jpg", image_format="JPEG", size=(20, 20)):
    """Membuat gambar sementara untuk pengujian upload API."""
    buffer = BytesIO()
    Image.new("RGB", size, color="orange").save(
        buffer,
        format=image_format,
    )
    return SimpleUploadedFile(
        name,
        buffer.getvalue(),
        content_type="image/jpeg",
    )


class HealthEndpointTests(SimpleTestCase):
    """Pengujian endpoint kesehatan backend HealthCoach."""

    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint(self):
        response = self.client.get(reverse("api:health"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["status"], "ok")


class FoodAnalysisEndpointTests(SimpleTestCase):
    """Pengujian request, response, dan error endpoint analisis."""

    def setUp(self):
        self.client = APIClient()

    # ==========================================================
    # 1. VALIDASI INPUT FOTO
    # ==========================================================

    def test_images_are_required(self):
        response = self.client.post(
            reverse("api:analyze"),
            data={},
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(body["success"])
        self.assertEqual(
            body["error"]["code"],
            "VALIDATION_ERROR",
        )

    @override_settings(MAX_UPLOAD_IMAGES=2)
    def test_rejects_too_many_images(self):
        response = self.client.post(
            reverse("api:analyze"),
            data={
                "images": [
                    make_image("one.jpg"),
                    make_image("two.jpg"),
                    make_image("three.jpg"),
                ]
            },
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(body["success"])
        self.assertEqual(
            body["error"]["code"],
            "VALIDATION_ERROR",
        )

    # ==========================================================
    # 2. PENANGANAN ERROR GEMINI MELALUI API
    # ==========================================================

    @override_settings(GEMINI_API_KEY="")
    def test_missing_api_key_returns_safe_service_error(self):
        response = self.client.post(
            reverse("api:analyze"),
            data={"images": [make_image()]},
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 503)
        self.assertFalse(body["success"])
        self.assertEqual(
            body["error"]["code"],
            "GEMINI_NOT_CONFIGURED",
        )
        self.assertNotIn(
            "API_KEY",
            body["error"]["message"],
        )

    @patch(
        "api.views.analyze_food_images",
        side_effect=GeminiQuotaError(),
    )
    def test_quota_error_keeps_its_http_status(
        self,
        _analyze_mock,
    ):
        response = self.client.post(
            reverse("api:analyze"),
            data={"images": [make_image()]},
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 429)
        self.assertFalse(body["success"])
        self.assertEqual(
            body["error"]["code"],
            "GEMINI_QUOTA_EXCEEDED",
        )

    @patch(
        "api.views.analyze_food_images",
        side_effect=GeminiAuthenticationError(),
    )
    def test_access_error_is_not_reported_as_not_configured(
        self,
        _analyze_mock,
    ):
        response = self.client.post(
            reverse("api:analyze"),
            data={"images": [make_image()]},
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 502)
        self.assertFalse(body["success"])
        self.assertEqual(
            body["error"]["code"],
            "GEMINI_ACCESS_DENIED",
        )

    # ==========================================================
    # 3. RESPONS SUKSES ANALISIS MAKANAN
    # ==========================================================

    @patch("api.views.analyze_food_images")
    def test_returns_consistent_success_payload(
        self,
        analyze_mock,
    ):
        analyze_mock.return_value = {
            "identification": {
                "food_name": "Nasi Goreng",
                "canonical_food_name": "Nasi Goreng",
                "identification_status": "IDENTIFIED",
                "confidence": "tinggi",
                "ingredients": [],
                "notes": "",
            },
            "matching": {
                "normalized_name": "nasi goreng",
                "status": "MATCHED",
                "duplicate_count": 1,
                "method": "EXACT",
                "reference_name": None,
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
            "recommendation": (
                "Berdasarkan data nutrisi dataset HealthCoach, "
                "pilih porsi sesuai kebutuhan."
            ),
            "recommendation_details": {
                "saran": "Tambahkan sayuran sebagai pelengkap.",
                "alasan": "Data nutrisi tersedia pada dataset.",
                "pendamping_alternatif": (
                    "Sayuran segar dapat menjadi pilihan."
                ),
                "catatan_nutrisi": (
                    "Lihat panel nutrisi untuk data lengkap."
                ),
            },
            "note": "Informasi umum.",
        }

        response = self.client.post(
            reverse("api:analyze"),
            data={
                "images": [
                    make_image("front.jpg"),
                    make_image("side.jpg"),
                ]
            },
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertEqual(
            body["meta"]["images_received"],
            2,
        )
        self.assertTrue(body["meta"]["request_id"])
        self.assertEqual(
            body["data"]["identification"]["food_name"],
            "Nasi Goreng",
        )
        self.assertEqual(
            body["data"]["matching"]["status"],
            "MATCHED",
        )
        self.assertEqual(
            body["data"]["matching"]["method"],
            "EXACT",
        )
        self.assertEqual(
            body["data"]["nutrition"]["name"],
            "Nasi Goreng",
        )

        analyze_mock.assert_called_once()

    # ==========================================================
    # 4. KOMPATIBILITAS FRONTEND LAMA
    # ==========================================================

    @patch("api.views.analyze_food_images")
    def test_legacy_single_image_field_is_supported(
        self,
        analyze_mock,
    ):
        analyze_mock.return_value = {
            "identification": {},
            "matching": {},
            "nutrition": None,
            "recommendation": "",
            "recommendation_details": {},
            "note": "",
        }

        response = self.client.post(
            reverse("api:analyze"),
            data={"image": make_image()},
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertEqual(
            body["meta"]["images_received"],
            1,
        )

        analyze_mock.assert_called_once()

    # ==========================================================
    # 5. CANONICAL MATCHING - PENGUJIAN BARU TIWI
    # ==========================================================

    @patch("api.views.analyze_food_images")
    def test_canonical_matching_response(self, analyze_mock):
        analyze_mock.return_value = {
            "identification": {
                "food_name": "Nasi Goreng Ayam",
                "canonical_food_name": "Nasi Goreng",
                "identification_status": "IDENTIFIED",
            },
            "matching": {
                "normalized_name": "nasi goreng ayam",
                "status": "MATCHED",
                "duplicate_count": 1,
                "method": "CANONICAL",
                "reference_name": "Nasi Goreng",
            },
            "nutrition": {
                "name": "Nasi Goreng",
                "calories": "276.0",
            },
            "recommendation": (
                "Tambahkan sayuran sebagai pendamping."
            ),
            "recommendation_details": {
                "saran": "Tambahkan sayuran.",
                "alasan": "Sebagai pelengkap hidangan.",
                "pendamping_alternatif": "Sayuran segar.",
                "catatan_nutrisi": (
                    "Nilai nutrisi berasal dari makanan referensi."
                ),
            },
            "note": (
                "Data nutrisi menggunakan referensi Nasi Goreng. "
                "Nilai sebenarnya dapat berbeda."
            ),
        }

        response = self.client.post(
            reverse("api:analyze"),
            data={"images": [make_image()]},
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertEqual(
            body["data"]["identification"]["food_name"],
            "Nasi Goreng Ayam",
        )
        self.assertEqual(
            body["data"]["matching"]["status"],
            "MATCHED",
        )
        self.assertEqual(
            body["data"]["matching"]["method"],
            "CANONICAL",
        )
        self.assertEqual(
            body["data"]["matching"]["reference_name"],
            "Nasi Goreng",
        )
        self.assertEqual(
            body["data"]["nutrition"]["name"],
            "Nasi Goreng",
        )
        self.assertIn(
            "referensi",
            body["data"]["note"].lower(),
        )

        analyze_mock.assert_called_once()

    # ==========================================================
    # 6. UNKNOWN TANPA NUTRISI - PENGUJIAN BARU TIWI
    # ==========================================================

    @patch("api.views.analyze_food_images")
    def test_unknown_food_returns_no_nutrition(
        self,
        analyze_mock,
    ):
        analyze_mock.return_value = {
            "identification": {
                "food_name": None,
                "canonical_food_name": None,
                "identification_status": "UNKNOWN",
            },
            "matching": {
                "normalized_name": "",
                "status": "NOT_MATCHED",
                "duplicate_count": 0,
                "method": None,
                "reference_name": None,
            },
            "nutrition": None,
            "recommendation": (
                "Foto belum dapat dikenali sebagai makanan."
            ),
            "recommendation_details": {
                "saran": "Ambil ulang foto yang lebih jelas.",
                "alasan": "Objek belum dapat dikenali.",
                "pendamping_alternatif": "Tidak tersedia.",
                "catatan_nutrisi": "Tidak ada data nutrisi.",
            },
            "note": "Tidak ada data nutrisi.",
        }

        response = self.client.post(
            reverse("api:analyze"),
            data={"images": [make_image()]},
            format="multipart",
        )

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertEqual(
            body["data"]["identification"][
                "identification_status"
            ],
            "UNKNOWN",
        )
        self.assertEqual(
            body["data"]["matching"]["status"],
            "NOT_MATCHED",
        )
        self.assertIsNone(
            body["data"]["nutrition"]
        )
        self.assertIsNone(
            body["data"]["matching"]["reference_name"]
        )

        analyze_mock.assert_called_once()

    # ==========================================================
    # 7. INVALID GEMINI RESPONSE - PENGUJIAN BARU TIWI
    # ==========================================================

    @patch(
        "api.views.analyze_food_images",
        side_effect=GeminiResponseError(),
    )
    def test_invalid_gemini_response_returns_safe_error(
        self,
        _analyze_mock,
    ):
        response = self.client.post(
            reverse("api:analyze"),
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
        self.assertEqual(
            body["error"]["message"],
            "Layanan AI memberikan respons yang tidak dapat diproses.",
        )
        self.assertIsNone(
            body["error"]["details"]
        )
        self.assertNotIn(
            "Traceback",
            body["error"]["message"],
        )
