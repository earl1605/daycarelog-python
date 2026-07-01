from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()
router.register("children", views.ChildViewSet, basename="child")
router.register("guardians", views.GuardianProfileViewSet, basename="guardian")
router.register("health-records", views.HealthRecordViewSet, basename="health-record")
router.register("attendance", views.AttendanceViewSet, basename="attendance")

urlpatterns = [
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/me/", views.MeView.as_view(), name="me"),
    path("users/", views.StaffAccountListCreateView.as_view(), name="users"),
    path("dashboard/stats/", views.DashboardStatsView.as_view(), name="dashboard-stats"),
    path("", include(router.urls)),
]
