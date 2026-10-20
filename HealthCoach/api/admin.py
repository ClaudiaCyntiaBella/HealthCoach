
"""Konfigurasi Dashboard Admin HealthCoach - Issue #56."""

from django.contrib import admin

from .models import Nutrition


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
