
from django.contrib import admin
from django.urls import include, path

from dashboard.views import dashboard_home


urlpatterns = [
    path("", dashboard_home, name="home"),
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    path("api/v1/", include("api.urls")),
]
