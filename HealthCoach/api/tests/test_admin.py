
"""Pengujian Django Admin HealthCoach - Issue #56."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from api.models import Nutrition


User = get_user_model()


class NutritionAdminTests(TestCase):
    """Pengujian dashboard admin nutrisi."""

    def setUp(self):
        self.list_url = reverse("admin:api_nutrition_changelist")

        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            email="admin_test@example.com",
            password="Admin!2026SehatBiru",
        )

        self.nasi_goreng = Nutrition.objects.create(
            id=10001,
            name="Nasi Goreng",
            name_normalized="nasi goreng",
            calories=350.0,
            proteins=12.0,
            fat=10.0,
            carbohydrate=48.0,
        )

        Nutrition.objects.create(
            id=10002,
            name="Sate Ayam",
            name_normalized="sate ayam",
            calories=250.0,
            proteins=20.0,
            fat=12.0,
            carbohydrate=8.0,
        )

    def test_admin_requires_login(self):
        """Pengguna tanpa login diarahkan ke halaman login."""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_admin_can_view_and_search_food(self):
        """Admin bisa melihat dan mencari makanan."""
        self.client.force_login(self.admin_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nasi Goreng")
        self.assertContains(response, "Sate Ayam")

        search_response = self.client.get(
            self.list_url,
            {"q": "Nasi Goreng"},
        )

        self.assertEqual(search_response.status_code, 200)
        self.assertContains(search_response, "Nasi Goreng")
        self.assertNotContains(search_response, "Sate Ayam")

    def test_admin_can_view_nutrition_details(self):
        """Admin bisa melihat detail data nutrisi."""
        self.client.force_login(self.admin_user)

        detail_url = reverse(
            "admin:api_nutrition_change",
            args=[self.nasi_goreng.pk],
        )

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nasi Goreng")
        self.assertContains(response, "350")
        self.assertContains(response, "12")
        self.assertContains(response, "10")
        self.assertContains(response, "48")

    def test_regular_user_cannot_access_admin(self):
        """Pengguna biasa tidak dapat mengakses admin."""

        regular_user = User.objects.create_user(
            username="user_biasa",
            email="user_biasa@example.com",
            password="User!2026SehatBiru",
        )

        self.client.force_login(regular_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_staff_without_permission_cannot_view_nutrition(self):
        """Staff tanpa izin model nutrisi ditolak."""

        staff_user = User.objects.create_user(
            username="staff_test",
            email="staff_test@example.com",
            password="Staff!2026SehatBiru",
            is_staff=True,
        )

        self.client.force_login(staff_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)
