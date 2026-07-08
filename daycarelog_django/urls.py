from django.urls import include, path

from accounts.views import landing

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("api/", include("api.urls")),
    path("", landing, name="landing"),
]
