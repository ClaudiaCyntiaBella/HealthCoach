
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import render

from api.models import Nutrition


User = get_user_model()


@staff_member_required(login_url="/admin/login/")
def dashboard_home(request):
    total_nutrition = Nutrition.objects.count()
    total_users = User.objects.count()

    duplicate_groups = (
        Nutrition.objects
        .values("name_normalized")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
        .count()
    )

    context = {
        "page_title": "Dashboard Overview",
        "total_nutrition": total_nutrition,
        "total_users": total_users,
        "duplicate_groups": duplicate_groups,
        "total_analyses": 0,
    }

    return render(request, "dashboard/index.html", context)
