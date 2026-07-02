from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import DaycareLoginForm, ParentRegistrationForm


def landing(request):
    return render(request, "landing.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:redirect_after_login")

    if request.method == "POST":
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please sign in.")
            return redirect("accounts:login")
    else:
        form = ParentRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


class DaycareLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = DaycareLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("accounts:redirect_after_login")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid email or password.")
        return super().form_invalid(form)


def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


def redirect_after_login(request):
    user = request.user
    if not user.is_authenticated:
        return redirect("accounts:login")
    if user.is_staff_role:
        return redirect("dashboard:home")
    return redirect("dashboard:parent_home")
