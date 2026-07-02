from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("children/", views.children_list, name="children_list"),
    path("children/<int:pk>/edit/", views.child_edit, name="child_edit"),
    path("children/<int:pk>/delete/", views.child_delete, name="child_delete"),
    path("guardians/", views.guardians_list, name="guardians_list"),
    path("guardians/<int:pk>/edit/", views.guardian_edit, name="guardian_edit"),
    path("guardians/<int:pk>/delete/", views.guardian_delete, name="guardian_delete"),
    path("health-records/", views.health_records_list, name="health_records_list"),
    path("health-records/<int:pk>/edit/", views.health_record_edit, name="health_record_edit"),
    path("health-records/<int:pk>/delete/", views.health_record_delete, name="health_record_delete"),
    path("attendance/", views.attendance_list, name="attendance_list"),
    path("attendance/<int:pk>/edit/", views.attendance_edit, name="attendance_edit"),
    path("attendance/<int:pk>/delete/", views.attendance_delete, name="attendance_delete"),
    path("accounts-management/", views.account_management, name="account_management"),
    path("reports/", views.reports, name="reports"),
    path("reports/export/", views.reports_export_csv, name="reports_export_csv"),
    path("settings/", views.settings_view, name="settings"),
    path("parent/", views.parent_home, name="parent_home"),
]
