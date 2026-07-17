from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


@patch("accounts.forms.has_mx_record", return_value=True)
class RegistrationWorkflowTests(TestCase):
    """Workflow: a new user registers through the public form (which always
    creates a STAFF account - parent accounts are staff-provisioned only,
    see dashboard.forms.GuardianAccountCreateForm) and can sign in
    immediately afterwards."""

    def _register(self, email="newstaff@daycare.test"):
        return self.client.post(reverse("accounts:register"), {
            "first_name": "New", "last_name": "Staffer", "middle_name": "", "suffix": "",
            "email": email, "contact_number": "09171234567",
            "password": "supersecret1", "confirm_password": "supersecret1",
        })

    def test_register_and_login_workflow(self, mock_has_mx_record):
        response = self._register()
        user = User.objects.get(email="newstaff@daycare.test")
        self.assertEqual(user.role, User.Role.STAFF)
        self.assertRedirects(response, reverse("accounts:login"))

        response = self.client.post(reverse("accounts:login"), {
            "username": "newstaff@daycare.test", "password": "supersecret1",
        })
        self.assertIn("_auth_user_id", self.client.session)

    def test_registering_with_duplicate_email_is_rejected(self, mock_has_mx_record):
        User.objects.create_user(
            username="dup@daycare.test", email="dup@daycare.test", password="testpass123",
            role=User.Role.STAFF,
        )
        response = self._register(email="dup@daycare.test")
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", "An account with this email already exists."
        )
        self.assertEqual(User.objects.filter(email="dup@daycare.test").count(), 1)
