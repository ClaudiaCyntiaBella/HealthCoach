"""Serializer riwayat analisis makanan HealthCoach."""

from rest_framework import serializers

from .models import FoodAnalysisHistory


class FoodAnalysisHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAnalysisHistory
        fields = ["id", "result", "created_at"]
        read_only_fields = fields