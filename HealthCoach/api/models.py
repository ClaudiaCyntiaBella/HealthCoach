
"""Model database nutrisi, riwayat analisis, dan profil kesehatan pengguna."""

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
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
        related_name="analysis_histories",
    )
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "food_analysis_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Riwayat {self.user.username} - {self.created_at}"


class UserHealthProfile(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    ACTIVITY_LEVEL_CHOICES = [
        ("sedentary", "Sedentary"),
        ("light", "Lightly Active"),
        ("moderate", "Moderately Active"),
        ("active", "Active"),
        ("very_active", "Very Active"),
    ]

    NUTRITION_GOAL_CHOICES = [
        ("lose_weight", "Lose Weight"),
        ("maintain_weight", "Maintain Weight"),
        ("gain_weight", "Gain Weight"),
        ("healthy_eating", "Healthy Eating"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="health_profile",
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(500),
        ],
    )

    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(30),
            MaxValueValidator(300),
        ],
    )

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        default="",
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
    )

    activity_level = models.CharField(
        max_length=20,
        choices=ACTIVITY_LEVEL_CHOICES,
        blank=True,
        default="",
    )

    nutrition_goal = models.CharField(
        max_length=20,
        choices=NUTRITION_GOAL_CHOICES,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_health_profiles"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Profil kesehatan {self.user.username}"
