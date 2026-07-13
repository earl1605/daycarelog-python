from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.DaycareLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("redirect/", views.redirect_after_login, name="redirect_after_login"),
    path("verify-email/", views.verify_email_pending, name="verify_email_pending"),
    path("verify-email/code/", views.verify_email_code, name="verify_email_code"),
    path("verify-email/resend/", views.resend_verification, name="resend_verification"),
    path("verify-email/<str:token>/", views.verify_email_link, name="verify_email_link"),
]
