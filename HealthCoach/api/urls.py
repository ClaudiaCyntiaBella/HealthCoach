from django.urls import path

from .views import FoodAnalysisView, HealthView


app_name = "api"

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("analyze/", FoodAnalysisView.as_view(), name="analyze"),
]

