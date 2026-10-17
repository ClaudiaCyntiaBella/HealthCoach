
"""Daftar endpoint API HealthCoach."""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .auth_views import (
    LogoutView,
    ProfileView,
    RegisterView,
)
from .views import FoodAnalysisView, HealthView


app_name = "api"

urlpatterns = [
    # Endpoint HealthCoach yang sudah tersedia
    path(
        "health/",
        HealthView.as_view(),
        name="health",
    ),
    path(
        "analyze/",
        FoodAnalysisView.as_view(),
        name="analyze",
    ),

    # Issue #54 - Registrasi pengguna
    path(
        "auth/register/",
        RegisterView.as_view(),
        name="register",
    ),

    # Issue #54 - Login JWT
    path(
        "auth/login/",
        TokenObtainPairView.as_view(),
        name="login",
    ),

    # Issue #54 - Refresh access token
    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="refresh",
    ),

    # Issue #54 - Logout pengguna
    path(
        "auth/logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    # Issue #54 - Profil pengguna yang sudah login
    path(
        "auth/me/",
        ProfileView.as_view(),
        name="profile",
    ),
]
