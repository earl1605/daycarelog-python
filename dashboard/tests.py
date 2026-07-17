from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from enrollment.models import Attendance, Child, GuardianProfile, HealthRecord, Immunization

User = get_user_model()


def make_staff(email="staff@daycare.test", **extra):
    return User.objects.create_user(
        username=email, email=email, password="testpass123",
        role=User.Role.STAFF, is_staff=True, **extra
    )


def make_parent(email="parent@daycare.test", **extra):
    return User.objects.create_user(
        username=email, email=email, password="testpass123",
        role=User.Role.PARENT, **extra
    )


def next_weekday(start=None):
    """First weekday (Mon-Fri) on or after `start` (default: today) - the
    Attendance model rejects weekend dates."""
    day = start or date.today()
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day


class StaffChildLifecycleWorkflowTests(TestCase):
    """Workflow 1: staff provisions a parent account, enrolls a child under
    it, and logs attendance, a health record, and an immunization for that
    child - the core daycare-log feature exercised end to end through the
    dashboard UI, not the admin panel."""

    def setUp(self):
        self.staff = make_staff()
        self.client.login(username="staff@daycare.test", password="testpass123")

    def test_full_enrollment_and_logging_workflow(self):
        response = self.client.post(reverse("dashboard:guardians_list"), {
            "first_name": "Pat", "last_name": "Reyes", "middle_name": "", "suffix": "",
            "email": "pat@daycare.test", "contact_number": "09171234567",
            "address": "123 Main St", "relationship_to_child": "Mother",
        })
        self.assertEqual(response.status_code, 200)
        guardian = GuardianProfile.objects.get(user__email="pat@daycare.test")

        response = self.client.post(reverse("dashboard:children_list"), {
            "guardian": guardian.id, "first_name": "Timmy", "last_name": "Reyes",
            "date_of_birth": "2022-05-01", "sex": "M", "status": "ENROLLED",
            "blood_type": "", "medical_conditions": "",
        })
        self.assertRedirects(response, reverse("dashboard:children_list"))
        child = Child.objects.get(first_name="Timmy")

        attendance_date = next_weekday()
        response = self.client.post(reverse("dashboard:attendance_list"), {
            "child": child.id, "date": attendance_date.isoformat(),
            "status": "PRESENT", "remarks": "",
        })
        self.assertRedirects(response, reverse("dashboard:attendance_list"))
        self.assertTrue(Attendance.objects.filter(child=child, date=attendance_date).exists())

        response = self.client.post(reverse("dashboard:health_records_list"), {
            "child": child.id, "record_date": attendance_date.isoformat(),
            "height_cm": "90.5", "weight_kg": "13.2", "temperature_c": "36.8",
            "allergies": "", "notes": "",
        })
        self.assertRedirects(response, reverse("dashboard:health_records_list"))
        self.assertEqual(HealthRecord.objects.get(child=child).recorded_by, self.staff)

        response = self.client.post(reverse("dashboard:immunizations_list"), {
            "child": child.id, "vaccine_name": "BCG", "dose_number": "1",
            "date_given": attendance_date.isoformat(), "administered_by": "Nurse Joy", "notes": "",
        })
        self.assertRedirects(response, reverse("dashboard:immunizations_list"))
        self.assertTrue(Immunization.objects.filter(child=child, vaccine_name="BCG").exists())

        response = self.client.get(reverse("dashboard:child_detail", args=[child.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Timmy")

        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.context["active_count"], 1)
        self.assertEqual(response.context["present_today"], 1)


class ParentAccessWorkflowTests(TestCase):
    """Workflow 2: a staff-provisioned parent logs in with their temp
    password and can see only their own child's attendance, health, and
    immunization records - never another parent's."""

    def setUp(self):
        self.staff = make_staff()
        self.parent_a = make_parent("parenta@daycare.test")
        self.parent_b = make_parent("parentb@daycare.test")
        self.guardian_a = GuardianProfile.objects.create(
            user=self.parent_a, relationship_to_child="Father"
        )
        self.child_a = Child.objects.create(
            guardian=self.guardian_a, first_name="Amy", last_name="A",
            date_of_birth=date(2020, 1, 1), sex="F", status=Child.Status.ENROLLED,
        )
        self.attendance_date = next_weekday()
        Attendance.objects.create(
            child=self.child_a, date=self.attendance_date, status=Attendance.Status.PRESENT
        )

    def test_parent_sees_only_their_own_childs_records(self):
        self.client.login(username="parenta@daycare.test", password="testpass123")

        response = self.client.get(reverse("dashboard:parent_home"))
        self.assertContains(response, "Amy")

        response = self.client.get(reverse("dashboard:parent_attendance_list"))
        self.assertContains(response, "Amy")

        response = self.client.get(reverse("dashboard:child_detail", args=[self.child_a.id]))
        self.assertEqual(response.status_code, 200)

    def test_parent_cannot_view_another_parents_child(self):
        self.client.login(username="parentb@daycare.test", password="testpass123")

        response = self.client.get(reverse("dashboard:parent_home"))
        self.assertNotContains(response, "Amy")

        response = self.client.get(reverse("dashboard:child_detail", args=[self.child_a.id]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse("dashboard:parent_attendance_list"))
        self.assertNotContains(response, "Amy")

    def test_parent_cannot_access_staff_only_pages(self):
        self.client.login(username="parenta@daycare.test", password="testpass123")
        response = self.client.get(reverse("dashboard:children_list"))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("dashboard:account_management"))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("dashboard:reports"))
        self.assertEqual(response.status_code, 403)


class ValidationAndDuplicateRecordTests(TestCase):
    """Workflow 3 (negative paths): duplicate attendance/immunization
    submissions and out-of-range or malformed input are rejected by
    validation instead of corrupting the log."""

    def setUp(self):
        self.staff = make_staff()
        self.parent = make_parent()
        self.guardian = GuardianProfile.objects.create(
            user=self.parent, relationship_to_child="Mother"
        )
        self.child = Child.objects.create(
            guardian=self.guardian, first_name="Ben", last_name="B",
            date_of_birth=date(2021, 6, 1), sex="M", status=Child.Status.ENROLLED,
        )
        self.attendance_date = next_weekday()
        self.client.login(username="staff@daycare.test", password="testpass123")

    def test_duplicate_attendance_record_is_rejected(self):
        Attendance.objects.create(
            child=self.child, date=self.attendance_date, status=Attendance.Status.PRESENT
        )
        response = self.client.post(reverse("dashboard:attendance_list"), {
            "child": self.child.id, "date": self.attendance_date.isoformat(),
            "status": "LATE", "remarks": "resubmit",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(
            Attendance.objects.filter(child=self.child, date=self.attendance_date).count(), 1
        )

    def test_weekend_attendance_is_rejected(self):
        saturday = self.attendance_date
        while saturday.weekday() != 5:
            saturday += timedelta(days=1)
        response = self.client.post(reverse("dashboard:attendance_list"), {
            "child": self.child.id, "date": saturday.isoformat(),
            "status": "PRESENT", "remarks": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "date",
            "Attendance can only be recorded for weekdays (Monday–Friday).",
        )
        self.assertFalse(Attendance.objects.filter(child=self.child, date=saturday).exists())

    def test_duplicate_immunization_dose_is_rejected(self):
        Immunization.objects.create(
            child=self.child, vaccine_name="BCG", dose_number=1,
            date_given=self.attendance_date, recorded_by=self.staff,
        )
        response = self.client.post(reverse("dashboard:immunizations_list"), {
            "child": self.child.id, "vaccine_name": "BCG", "dose_number": "1",
            "date_given": self.attendance_date.isoformat(), "administered_by": "", "notes": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Immunization.objects.filter(child=self.child, vaccine_name="BCG").count(), 1
        )

    def test_out_of_range_health_record_values_are_rejected(self):
        response = self.client.post(reverse("dashboard:health_records_list"), {
            "child": self.child.id, "record_date": self.attendance_date.isoformat(),
            "height_cm": "90", "weight_kg": "13", "temperature_c": "60",
            "allergies": "", "notes": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "temperature_c",
            "Ensure this value is less than or equal to 45.",
        )
        self.assertFalse(HealthRecord.objects.filter(child=self.child).exists())

    def test_invalid_contact_number_format_is_rejected(self):
        response = self.client.post(reverse("dashboard:guardians_list"), {
            "first_name": "Bad", "last_name": "Number", "middle_name": "", "suffix": "",
            "email": "badnumber@daycare.test", "contact_number": "12345",
            "address": "", "relationship_to_child": "Father",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "contact_number",
            "Enter a valid PH mobile number (e.g. 09171234567).",
        )
        self.assertFalse(User.objects.filter(email="badnumber@daycare.test").exists())
