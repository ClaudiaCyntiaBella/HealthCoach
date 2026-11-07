
"""Endpoint API profil kesehatan pengguna HealthCoach."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserHealthProfile
from .health_profile_serializers import UserHealthProfileSerializer


class UserHealthProfileView(APIView):
    """Mengambil, membuat, dan memperbarui profil kesehatan."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Mengambil profil kesehatan pengguna yang login."""

        profile = UserHealthProfile.objects.filter(
            user=request.user
        ).first()

        if profile is None:
            return Response(
                {
                    "success": True,
                    "data": None,
                    "message": "Profil kesehatan belum diisi.",
                },
                status=status.HTTP_200_OK,
            )

        serializer = UserHealthProfileSerializer(profile)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Membuat profil kesehatan pertama kali."""

        serializer = UserHealthProfileSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # OneToOneField pada model memastikan satu
        # pengguna hanya memiliki satu profil.
        # get_or_create juga menangani pembuatan
        # secara aman jika request terjadi bersamaan.
        profile, created = UserHealthProfile.objects.get_or_create(
            user=request.user,
            defaults=serializer.validated_data,
        )

        if not created:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "PROFILE_ALREADY_EXISTS",
                        "message": (
                            "Profil kesehatan sudah tersedia. "
                            "Gunakan PATCH untuk memperbaruinya."
                        ),
                        "details": None,
                    },
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "success": True,
                "message": "Profil kesehatan berhasil dibuat.",
                "data": UserHealthProfileSerializer(profile).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request):
        """Memperbarui sebagian data profil kesehatan."""

        profile = get_object_or_404(
            UserHealthProfile,
            user=request.user,
        )

        serializer = UserHealthProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Profil kesehatan berhasil diperbarui.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
