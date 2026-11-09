
"""Serializer autentikasi pengguna HealthCoach - Issue #54."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "Email sudah terdaftar. Gunakan email lain."
            )

        return email

    def validate(self, attrs):
        user = User(
            username=attrs["username"],
            email=attrs["email"],
        )

        try:
            validate_password(
                attrs["password"],
                user=user,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {"password": exc.messages}
            ) from exc

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Validasi perubahan profil pengguna yang sedang login."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "email": {
                "required": False,
                "allow_blank": False,
            },
        }

    def validate_username(self, value):
        username = value.strip()

        if User.objects.filter(
            username__iexact=username
        ).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError(
                "Username sudah digunakan pengguna lain."
            )

        return username

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError(
                "Email sudah terdaftar. Gunakan email lain."
            )

        return email

    def validate(self, attrs):
        allowed_fields = {
            "username",
            "email",
            "first_name",
            "last_name",
        }

        unknown_fields = set(self.initial_data.keys()) - allowed_fields

        if unknown_fields:
            raise serializers.ValidationError({
                "non_field_errors": [
                    "Field tidak diizinkan: "
                    + ", ".join(sorted(unknown_fields))
                ]
            })

        if not attrs:
            raise serializers.ValidationError(
                "Minimal satu data profil harus diisi."
            )

        return attrs
