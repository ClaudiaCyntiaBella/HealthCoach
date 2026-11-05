
"""Model database nutrisi dan riwayat analisis pengguna."""

from django.conf import settings
from django.db import models


class Nutrition(models.Model):
    id = models.BigIntegerField(primary_key=True)
    calories = models.FloatField()
    proteins = models.FloatField()
    fat = models.FloatField()
    carbohydrate = models.FloatField()
    name = models.CharField(max_length=255)
    image = models.URLField(max_length=1000, blank=True, default="")
    name_normalized = models.CharField(max_length=255, db_index=True)

    class Meta:
        db_table = "nutrition"
        ordering = ["id"]

    def __str__(self):
        return self.name


class FoodAnalysisHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analysis_histories"
    )
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "food_analysis_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Riwayat {self.user.username} - {self.created_at}"
