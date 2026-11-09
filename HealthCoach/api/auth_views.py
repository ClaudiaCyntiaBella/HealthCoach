
"""API autentikasi pengguna HealthCoach - Issue #54."""

from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .auth_serializers import RegisterSerializer, ProfileUpdateSerializer


class RegisterView(APIView):
    """Endpoint untuk registrasi pengguna baru."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Registrasi berhasil.",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )



class LogoutView(APIView):
    """Logout menggunakan refresh token yang masih valid."""

    # Logout tidak memerlukan access token.
    # Token yang kedaluwarsa pada header Authorization
    # tidak akan menghalangi proses logout.
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("refresh")

        if not isinstance(token, str) or not token.strip():
            raise ValidationError(
                {"refresh": ["Refresh token wajib diisi."]}
            )

        try:
            refresh_token = RefreshToken(token)
        except TokenError as exc:
            raise ValidationError(
                {
                    "refresh": [
                        "Refresh token tidak valid atau kedaluwarsa."
                    ]
                }
            ) from exc

        try:
            refresh_token.blacklist()
        except TokenError as exc:
            raise ValidationError(
                {
                    "refresh": [
                        "Refresh token tidak dapat dinonaktifkan."
                    ]
                }
            ) from exc

        return Response(
            {
                "success": True,
                "message": "Logout berhasil.",
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    """Menampilkan dan memperbarui profil pengguna yang login."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Mengambil data profil pengguna yang sedang login."""
        serializer = ProfileUpdateSerializer(request.user)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        """Memperbarui sebagian data profil pengguna."""
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Profil berhasil diperbarui.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
