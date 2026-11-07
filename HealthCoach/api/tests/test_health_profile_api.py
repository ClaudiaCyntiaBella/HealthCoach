
"""Pengujian API profil kesehatan HealthCoach."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import UserHealthProfile


User = get_user_model()


class HealthProfileAPITests(TestCase):
    """Pengujian GET, POST, PATCH, validasi, dan keamanan."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("api:health-profile")

        self.user = User.objects.create_user(
            username="tiwi_health_test",
            email="tiwi_health@example.com",
            password="PasswordUji!2026",
        )

        self.other_user = User.objects.create_user(
            username="user_lain_health",
            email="user_lain_health@example.com",
            password="PasswordUji!2026",
        )

        access_token = RefreshToken.for_user(
            self.user
        ).access_token

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        self.valid_data = {
            "weight": "65.50",
            "height": "170.00",
            "gender": "female",
            "birth_date": "2003-05-20",
            "activity_level": "moderate",
            "nutrition_goal": "maintain_weight",
        }

    def test_get_profile_not_created_yet(self):
        """GET tidak membuat profil kosong."""

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertIsNone(response.data["data"])

        self.assertFalse(
            UserHealthProfile.objects.filter(
                user=self.user
            ).exists()
        )

    def test_authentication_required(self):
        """GET, POST, dan PATCH wajib login."""

        self.client.credentials()

        requests = [
            ("GET", {}),
            ("POST", self.valid_data),
            ("PATCH", {"weight": "70.00"}),
        ]

        for method, data in requests:
            with self.subTest(method=method):
                response = getattr(
                    self.client,
                    method.lower()
                )(
                    self.url,
                    data=data,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    401,
                )

        self.assertEqual(
            UserHealthProfile.objects.count(),
            0,
        )

    def test_create_health_profile(self):
        """POST membuat profil pengguna login."""

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])

        profile = UserHealthProfile.objects.get(
            user=self.user
        )

        self.assertEqual(profile.gender, "female")
        self.assertEqual(
            profile.nutrition_goal,
            "maintain_weight",
        )

        self.assertEqual(
            UserHealthProfile.objects.count(),
            1,
        )

    def test_duplicate_profile_rejected(self):
        """POST kedua tidak membuat duplikat."""

        first = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        second = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)

        self.assertEqual(
            UserHealthProfile.objects.filter(
                user=self.user
            ).count(),
            1,
        )

    def test_get_existing_profile(self):
        """GET mengembalikan profil pemilik akun."""

        UserHealthProfile.objects.create(
            user=self.user,
            weight="65.50",
            height="170.00",
            gender="female",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["data"]["gender"],
            "female",
        )

    def test_patch_health_profile(self):
        """PATCH memperbarui sebagian data profil."""

        profile = UserHealthProfile.objects.create(
            user=self.user,
            weight="65.00",
            height="170.00",
            gender="female",
        )

        response = self.client.patch(
            self.url,
            {
                "weight": "68.50",
                "nutrition_goal": "healthy_eating",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

        profile.refresh_from_db()

        self.assertEqual(
            float(profile.weight),
            68.50,
        )

        self.assertEqual(
            profile.nutrition_goal,
            "healthy_eating",
        )

        self.assertEqual(profile.gender, "female")

    def test_patch_without_profile(self):
        """PATCH ditolak jika profil belum dibuat."""

        response = self.client.patch(
            self.url,
            {"weight": "70.00"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_invalid_weight_and_height(self):
        """Berat dan tinggi di luar batas ditolak."""

        invalid_cases = [
            {"weight": "0"},
            {"weight": "501"},
            {"height": "29"},
            {"height": "301"},
        ]

        for data in invalid_cases:
            with self.subTest(data=data):
                response = self.client.post(
                    self.url,
                    data,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    400,
                )

        self.assertFalse(
            UserHealthProfile.objects.filter(
                user=self.user
            ).exists()
        )

    def test_invalid_choices(self):
        """Nilai pilihan yang tidak dikenal ditolak."""

        invalid_cases = [
            {"gender": "unknown"},
            {"activity_level": "super_active"},
            {"nutrition_goal": "other_goal"},
        ]

        for data in invalid_cases:
            with self.subTest(data=data):
                response = self.client.post(
                    self.url,
                    data,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    400,
                )

    def test_future_birth_date_rejected(self):
        """Tanggal lahir masa depan ditolak."""

        future_date = (
            timezone.localdate() + timedelta(days=1)
        ).isoformat()

        response = self.client.post(
            self.url,
            {"birth_date": future_date},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_cannot_set_other_user_as_owner(self):
        """Frontend tidak boleh menentukan pemilik profil."""

        response = self.client.post(
            self.url,
            {
                "weight": "65.00",
                "user": self.other_user.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertFalse(
            UserHealthProfile.objects.filter(
                user=self.other_user
            ).exists()
        )

    def test_users_only_access_own_profile(self):
        """Data akun lain tidak boleh terbuka."""

        UserHealthProfile.objects.create(
            user=self.other_user,
            weight="80.00",
            gender="male",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["data"])

        response_patch = self.client.patch(
            self.url,
            {"weight": "60.00"},
            format="json",
        )

        self.assertEqual(
            response_patch.status_code,
            404,
        )

        other_profile = (
            UserHealthProfile.objects.get(
                user=self.other_user
            )
        )

        self.assertEqual(
            float(other_profile.weight),
            80.00,
        )

    def test_empty_request_rejected(self):
        """POST tanpa data kesehatan ditolak."""

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
