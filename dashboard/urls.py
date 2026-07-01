from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("children/", views.children_list, name="children_list"),
    path("guardians/", views.guardians_list, name="guardians_list"),
    path("health-records/", views.health_records_list, name="health_records_list"),
    path("attendance/", views.attendance_list, name="attendance_list"),
    path("accounts-management/", views.account_management, name="account_management"),
    path("parent/", views.parent_home, name="parent_home"),
]
