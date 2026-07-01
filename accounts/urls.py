from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.DaycareLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("redirect/", views.redirect_after_login, name="redirect_after_login"),
]
