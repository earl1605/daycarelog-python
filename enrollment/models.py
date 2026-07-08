from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class GuardianProfile(models.Model):
    """Extra fields for a User with role=PARENT."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guardian_profile",
        limit_choices_to={"role": "PARENT"},
    )
    address = models.CharField(max_length=255, blank=True)
    relationship_to_child = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.email


class Child(models.Model):
    class Sex(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    class Status(models.TextChoices):
        ENROLLED = "ENROLLED", "Enrolled"
        PENDING = "PENDING", "Pending"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    guardian = models.ForeignKey(
        GuardianProfile, on_delete=models.CASCADE, related_name="children"
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1, choices=Sex.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    enrollment_date = models.DateField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.date_of_birth and self.date_of_birth > timezone.localdate():
            raise ValidationError({"date_of_birth": "Date of birth cannot be in the future."})

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class HealthRecord(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="health_records")
    record_date = models.DateField()
    height_cm = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(250)],
    )
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(200)],
    )
    temperature_c = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(45)],
    )
    allergies = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        limit_choices_to={"role__in": ["STAFF", "ADMIN"]},
    )

    class Meta:
        ordering = ["-record_date"]

    def __str__(self):
        return f"{self.child} - {self.record_date}"


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("child", "date")
        ordering = ["-date"]

    def clean(self):
        super().clean()
        if self.date and self.date.weekday() >= 5:
            raise ValidationError({"date": "Attendance can only be recorded for weekdays (Monday–Friday)."})

    def __str__(self):
        return f"{self.child} - {self.date} ({self.status})"
