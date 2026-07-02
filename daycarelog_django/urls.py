from django.contrib import admin
from django.urls import include, path

from accounts.views import landing

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("api/", include("api.urls")),
    path("", landing, name="landing"),
]
