from django.contrib import messages
from django.contrib.auth import get_user_model, logout as auth_logout
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from accounts.emails import send_verification_email
from accounts.models import EmailVerification

from .forms import DaycareLoginForm, EmailVerificationCodeForm, PublicRegistrationForm

User = get_user_model()


def landing(request):
    return render(request, "landing.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:redirect_after_login")

    if request.method == "POST":
        form = PublicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            verification = EmailVerification.issue_for(user)
            send_verification_email(request, user, verification)
            return redirect(f"{reverse('accounts:verify_email_pending')}?email={user.email}")
    else:
        form = PublicRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def verify_email_pending(request):
    email = request.GET.get("email", "").strip()
    if not email:
        return redirect("accounts:login")
    return render(request, "accounts/verify_email_pending.html", {
        "form": EmailVerificationCodeForm(initial={"email": email}),
        "email": email,
    })


def verify_email_code(request):
    if request.method != "POST":
        return redirect("accounts:verify_email_pending")

    form = EmailVerificationCodeForm(request.POST)
    email = request.POST.get("email", "").strip()
    if form.is_valid():
        user = User.objects.filter(email__iexact=form.cleaned_data["email"]).first()
        verification = getattr(user, "email_verification", None) if user else None
        if verification and verification.code == form.cleaned_data["code"]:
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])
            messages.success(request, "Email verified! You can now sign in.")
            return redirect("accounts:login")
        form.add_error("code", "That code is incorrect or has expired.")

    return render(request, "accounts/verify_email_pending.html", {"form": form, "email": email})


def verify_email_link(request, token):
    verification = get_object_or_404(EmailVerification, token=token)
    user = verification.user
    if not user.is_email_verified:
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
    messages.success(request, "Email verified! You can now sign in.")
    return redirect("accounts:login")


def resend_verification(request):
    if request.method != "POST":
        return redirect("accounts:verify_email_pending")

    email = request.POST.get("email", "").strip()
    user = User.objects.filter(email__iexact=email).first()
    if user and not user.is_email_verified:
        verification = getattr(user, "email_verification", None)
        if verification and not verification.can_resend():
            messages.error(request, f"Please wait {verification.seconds_until_resend()}s before requesting another code.")
        else:
            verification = EmailVerification.issue_for(user)
            send_verification_email(request, user, verification)
            messages.success(request, "A new code has been sent to your email.")
    else:
        # Same message whether or not the address is registered/already
        # verified, so this endpoint can't be used to enumerate accounts.
        messages.success(request, "If that email needs verifying, a new code has been sent.")

    return redirect(f"{reverse('accounts:verify_email_pending')}?email={email}")


class DaycareLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = DaycareLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("accounts:redirect_after_login")

    def form_invalid(self, form):
        codes = [e.code for e in form.non_field_errors().as_data()]
        if "email_not_verified" in codes:
            email = form.cleaned_data.get("username", "")
            messages.error(self.request, "Please verify your email before signing in.")
            return redirect(f"{reverse('accounts:verify_email_pending')}?email={email}")
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
