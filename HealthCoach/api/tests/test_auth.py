
"""Pengujian API autentikasi HealthCoach - Issue #54."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()


class RegisterAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("api:register")

    def test_register_success(self):
        response = self.client.post(
            self.url,
            {
                "username": "tiwi_test",
                "email": "tiwi_test@example.com",
                "password": "Sehat!2026TamanBiru",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(response.data["success"])
        self.assertTrue(
            User.objects.filter(username="tiwi_test").exists()
        )

        user = User.objects.get(username="tiwi_test")
        self.assertTrue(user.check_password("Sehat!2026TamanBiru"))

    def test_register_weak_password(self):
        response = self.client.post(
            self.url,
            {
                "username": "tiwi_test",
                "email": "tiwi_test@example.com",
                "password": "123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            User.objects.filter(username="tiwi_test").exists()
        )

    def test_register_duplicate_email(self):
        User.objects.create_user(
            username="user_pertama",
            email="sama@example.com",
            password="Sehat!2026TamanBiru",
        )

        response = self.client.post(
            self.url,
            {
                "username": "user_kedua",
                "email": "sama@example.com",
                "password": "Sehat!2026TamanBiru",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            User.objects.filter(username="user_kedua").exists()
        )


class LoginAPITests(TestCase):
    """Pengujian login JWT - Issue #54."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("api:login")

        self.user = User.objects.create_user(
            username="tiwi_login",
            email="tiwi_login@example.com",
            password="Sehat!2026TamanBiru",
        )

    def test_login_success(self):
        response = self.client.post(
            self.url,
            {
                "username": "tiwi_login",
                "password": "Sehat!2026TamanBiru",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url,
            {
                "username": "tiwi_login",
                "password": "password_salah",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)


class RefreshTokenAPITests(TestCase):
    """Pengujian refresh token JWT - Issue #54."""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("api:login")
        self.refresh_url = reverse("api:refresh")

        User.objects.create_user(
            username="tiwi_refresh",
            email="tiwi_refresh@example.com",
            password="Sehat!2026TamanBiru",
        )

    def test_refresh_token_success(self):
        login_response = self.client.post(
            self.login_url,
            {
                "username": "tiwi_refresh",
                "password": "Sehat!2026TamanBiru",
            },
            format="json",
        )

        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)

    def test_refresh_token_invalid(self):
        response = self.client.post(
            self.refresh_url,
            {"refresh": "token_tidak_valid"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertNotIn("access", response.data)


class LogoutAPITests(TestCase):
    """Pengujian logout JWT - Issue #54."""

    def setUp(self):
        self.client = APIClient()
        self.logout_url = reverse("api:logout")
        self.refresh_url = reverse("api:refresh")

        self.user = User.objects.create_user(
            username="tiwi_logout",
            email="tiwi_logout@example.com",
            password="Sehat!2026TamanBiru",
        )

        from rest_framework_simplejwt.tokens import RefreshToken

        token = RefreshToken.for_user(self.user)
        self.refresh_token = str(token)
        self.access_token = str(token.access_token)

    def test_logout_success(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        response = self.client.post(
            self.logout_url,
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(response.data["success"])

        # Refresh token yang sudah logout harus ditolak.
        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_without_login(self):
        response = self.client.post(
            self.logout_url,
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_without_refresh_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        response = self.client.post(
            self.logout_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class ProfileAPITests(TestCase):
    """Pengujian proteksi endpoint profil - Issue #54."""

    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse("api:profile")

        self.user = User.objects.create_user(
            username="tiwi_profile",
            email="tiwi_profile@example.com",
            password="Sehat!2026TamanBiru",
        )

        from rest_framework_simplejwt.tokens import RefreshToken

        token = RefreshToken.for_user(self.user)
        self.access_token = str(token.access_token)

    def test_profile_with_valid_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        response = self.client.get(self.profile_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(response.data["success"])
        self.assertEqual(
            response.data["data"]["username"],
            "tiwi_profile",
        )
        self.assertEqual(
            response.data["data"]["email"],
            "tiwi_profile@example.com",
        )

    def test_profile_without_token(self):
        response = self.client.get(self.profile_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_profile_with_invalid_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer token_tidak_valid"
        )

        response = self.client.get(self.profile_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
