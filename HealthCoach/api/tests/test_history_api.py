
"""Pengujian endpoint riwayat analisis makanan HealthCoach."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from api.models import FoodAnalysisHistory


User = get_user_model()


class FoodAnalysisHistoryAPITests(TestCase):
    """Menguji autentikasi dan akses riwayat milik pengguna."""

    def setUp(self):
        self.client = APIClient()

        # Membuat dua pengguna khusus untuk pengujian
        self.user_a = User.objects.create_user(
            username="user_a_test",
            password="test-password-a",
        )
        self.user_b = User.objects.create_user(
            username="user_b_test",
            password="test-password-b",
        )

        # Membuat riwayat milik masing-masing pengguna
        self.history_a = FoodAnalysisHistory.objects.create(
            user=self.user_a,
            result={
                "identification": {
                    "food_name": "Nasi Goreng"
                },
                "nutrition_source": "DATASET",
            },
        )

        self.history_b = FoodAnalysisHistory.objects.create(
            user=self.user_b,
            result={
                "identification": {
                    "food_name": "Mie Goreng"
                },
                "nutrition_source": "AI_ESTIMATED",
            },
        )

    def login_as_user_a(self):
        self.client.force_authenticate(user=self.user_a)

    def test_history_requires_login(self):
        response = self.client.get(
            reverse("api:history-list")
        )

        self.assertIn(response.status_code, [401, 403])

    def test_user_can_view_own_history(self):
        self.login_as_user_a()

        response = self.client.get(
            reverse("api:history-list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        histories = response.json()["data"]
        history_ids = {item["id"] for item in histories}

        self.assertIn(self.history_a.id, history_ids)
        self.assertNotIn(self.history_b.id, history_ids)

    def test_user_can_view_own_history_detail(self):
        self.login_as_user_a()

        response = self.client.get(
            reverse(
                "api:history-detail",
                kwargs={"history_id": self.history_a.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["data"]["id"],
            self.history_a.id,
        )

    def test_user_cannot_view_other_user_history(self):
        self.login_as_user_a()

        response = self.client.get(
            reverse(
                "api:history-detail",
                kwargs={"history_id": self.history_b.id},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_user_can_delete_own_history(self):
        self.login_as_user_a()

        response = self.client.delete(
            reverse(
                "api:history-detail",
                kwargs={"history_id": self.history_a.id},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            FoodAnalysisHistory.objects.filter(
                id=self.history_a.id
            ).exists()
        )

        # Riwayat pengguna lain harus tetap ada
        self.assertTrue(
            FoodAnalysisHistory.objects.filter(
                id=self.history_b.id
            ).exists()
        )

    def test_user_cannot_delete_other_user_history(self):
        self.login_as_user_a()

        response = self.client.delete(
            reverse(
                "api:history-detail",
                kwargs={"history_id": self.history_b.id},
            )
        )

        self.assertEqual(response.status_code, 404)

        # Data pengguna B tidak boleh terhapus
        self.assertTrue(
            FoodAnalysisHistory.objects.filter(
                id=self.history_b.id
            ).exists()
        )
