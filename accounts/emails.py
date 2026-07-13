from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def send_verification_email(request, user, verification):
    """Sends both the clickable link and the 6-digit code - whichever the
    user finds easier to use verifies the account."""
    link = request.build_absolute_uri(
        reverse("accounts:verify_email_link", args=[verification.token])
    )
    subject = "Verify your DaycareLog account"
    message = (
        f"Hi {user.first_name or user.email},\n\n"
        f"Welcome to DaycareLog! Verify your email using either option below:\n\n"
        f"1. Click this link:\n{link}\n\n"
        f"2. Or enter this code on the verification page:\n{verification.code}\n\n"
        f"If you didn't create this account, you can ignore this email.\n"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
