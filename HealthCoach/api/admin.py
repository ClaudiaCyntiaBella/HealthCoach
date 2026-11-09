
"""Konfigurasi Admin HealthCoach."""

from django.contrib import admin

from .models import Nutrition, FoodAnalysisHistory, UserHealthProfile


@admin.register(Nutrition)
class NutritionAdmin(admin.ModelAdmin):
    """Menampilkan dan mencari data nutrisi makanan."""

    list_display = (
        "id",
        "name",
        "calories",
        "proteins",
        "fat",
        "carbohydrate",
    )

    search_fields = (
        "name",
        "name_normalized",
    )

    list_display_links = ("name",)

    ordering = ("name",)

    list_per_page = 25

    readonly_fields = (
        "id",
        "name",
        "name_normalized",
        "calories",
        "proteins",
        "fat",
        "carbohydrate",
        "image",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FoodAnalysisHistory)
class FoodAnalysisHistoryAdmin(admin.ModelAdmin):
    """Menampilkan riwayat analisis makanan pengguna."""

    list_display = (
        "id",
        "user",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    ordering = ("-created_at",)

    list_filter = ("created_at",)

    readonly_fields = (
        "user",
        "result",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserHealthProfile)
class UserHealthProfileAdmin(admin.ModelAdmin):
    """Mengelola profil kesehatan pengguna."""

    list_display = (
        "user",
        "weight",
        "height",
        "gender",
        "activity_level",
        "nutrition_goal",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    list_filter = (
        "gender",
        "activity_level",
        "nutrition_goal",
    )

    ordering = ("-updated_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )
