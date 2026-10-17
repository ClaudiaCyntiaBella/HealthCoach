
"""API autentikasi pengguna HealthCoach - Issue #54."""

from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .auth_serializers import RegisterSerializer


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
    """Endpoint logout dengan menonaktifkan refresh token."""

    permission_classes = [IsAuthenticated]

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
                {"refresh": ["Refresh token tidak valid atau kedaluwarsa."]}
            ) from exc

        if str(refresh_token.get("user_id")) != str(request.user.pk):
            raise PermissionDenied(
                "Refresh token bukan milik pengguna yang sedang login."
            )

        try:
            refresh_token.blacklist()
        except TokenError as exc:
            raise ValidationError(
                {"refresh": ["Refresh token tidak dapat dinonaktifkan."]}
            ) from exc

        return Response(
            {
                "success": True,
                "message": "Logout berhasil.",
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    """Menampilkan profil pengguna yang sudah login."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response(
            {
                "success": True,
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )
