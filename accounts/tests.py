from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from accounts.models import EmailVerification

User = get_user_model()


@patch("accounts.forms.has_mx_record", return_value=True)
class RegistrationAndVerificationWorkflowTests(TestCase):
    """Workflow: a new user registers through the public form (which always
    creates a STAFF account - parent accounts are staff-provisioned only,
    see dashboard.forms.GuardianAccountCreateForm), cannot sign in until
    they verify their email with the mailed 6-digit code, and can sign in
    immediately afterwards."""

    def _register(self, email="newstaff@daycare.test"):
        return self.client.post(reverse("accounts:register"), {
            "first_name": "New", "last_name": "Staffer", "middle_name": "", "suffix": "",
            "email": email, "contact_number": "09171234567",
            "password": "supersecret1", "confirm_password": "supersecret1",
        })

    def test_register_verify_and_login_workflow(self, mock_has_mx_record):
        response = self._register()
        user = User.objects.get(email="newstaff@daycare.test")
        self.assertEqual(user.role, User.Role.STAFF)
        self.assertFalse(user.is_email_verified)
        self.assertRedirects(
            response,
            f"{reverse('accounts:verify_email_pending')}?email=newstaff@daycare.test",
        )
        self.assertEqual(len(mail.outbox), 1)

        # Invalid action: signing in before verifying must be rejected, even
        # with the correct password.
        response = self.client.post(reverse("accounts:login"), {
            "username": "newstaff@daycare.test", "password": "supersecret1",
        })
        self.assertNotIn("_auth_user_id", self.client.session)

        verification = EmailVerification.objects.get(user=user)
        response = self.client.post(reverse("accounts:verify_email_code"), {
            "email": user.email, "code": verification.code,
        })
        self.assertRedirects(response, reverse("accounts:login"))
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)

        response = self.client.post(reverse("accounts:login"), {
            "username": "newstaff@daycare.test", "password": "supersecret1",
        })
        self.assertIn("_auth_user_id", self.client.session)

    def test_wrong_verification_code_is_rejected(self, mock_has_mx_record):
        self._register(email="badcode@daycare.test")
        response = self.client.post(reverse("accounts:verify_email_code"), {
            "email": "badcode@daycare.test", "code": "000000",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "code", "That code is incorrect or has expired."
        )
        user = User.objects.get(email="badcode@daycare.test")
        self.assertFalse(user.is_email_verified)

    def test_registering_with_duplicate_email_is_rejected(self, mock_has_mx_record):
        User.objects.create_user(
            username="dup@daycare.test", email="dup@daycare.test", password="testpass123",
            role=User.Role.STAFF, is_email_verified=True,
        )
        response = self._register(email="dup@daycare.test")
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", "An account with this email already exists."
        )
        self.assertEqual(User.objects.filter(email="dup@daycare.test").count(), 1)
