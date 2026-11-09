
"""Serializer untuk API profil kesehatan pengguna HealthCoach."""

from django.utils import timezone
from rest_framework import serializers

from .models import UserHealthProfile


class UserHealthProfileSerializer(serializers.ModelSerializer):
    """Validasi dan serialisasi profil kesehatan pengguna."""

    class Meta:
        model = UserHealthProfile

        fields = [
            "id",
            "weight",
            "height",
            "gender",
            "birth_date",
            "activity_level",
            "nutrition_goal",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_weight(self, value):
        """Berat badan harus 1–500 kg."""
        if value is not None and not (1 <= value <= 500):
            raise serializers.ValidationError(
                "Berat badan harus antara 1 sampai 500 kg."
            )
        return value

    def validate_height(self, value):
        """Tinggi badan harus 30–300 cm."""
        if value is not None and not (30 <= value <= 300):
            raise serializers.ValidationError(
                "Tinggi badan harus antara 30 sampai 300 cm."
            )
        return value

    def validate_birth_date(self, value):
        """Tanggal lahir tidak boleh di masa depan."""
        if value is not None and value > timezone.localdate():
            raise serializers.ValidationError(
                "Tanggal lahir tidak boleh di masa depan."
            )
        return value

    def validate(self, attrs):
        """Tolak field asing dan request tanpa data kesehatan."""

        allowed_fields = {
            "weight",
            "height",
            "gender",
            "birth_date",
            "activity_level",
            "nutrition_goal",
        }

        incoming_fields = set(self.initial_data.keys())
        unknown_fields = incoming_fields - allowed_fields

        if unknown_fields:
            raise serializers.ValidationError({
                "non_field_errors": [
                    "Field tidak diizinkan: "
                    + ", ".join(sorted(unknown_fields))
                ]
            })

        if not attrs:
            raise serializers.ValidationError(
                "Minimal satu data profil kesehatan harus diisi."
            )

        return attrs
