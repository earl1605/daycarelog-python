from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

contact_number_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message="Enter a valid PH mobile number (e.g. 09171234567).",
)


class User(AbstractUser):
    class Role(models.TextChoices):
        PARENT = "PARENT", "Parent/Guardian"
        STAFF = "STAFF", "Staff/BHW"
        ADMIN = "ADMIN", "Admin"

    class Suffix(models.TextChoices):
        NONE = "", "— None —"
        JR = "Jr.", "Jr."
        SR = "Sr.", "Sr."
        II = "II", "II"
        III = "III", "III"
        IV = "IV", "IV"
        V = "V", "V"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PARENT)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(
        max_length=20, blank=True, validators=[contact_number_validator]
    )
    middle_name = models.CharField(max_length=150, blank=True)
    suffix = models.CharField(max_length=10, choices=Suffix.choices, blank=True)
    # Stored as a base64 data URI (resized client-side to ~256px before upload),
    # not a file path - Vercel's serverless filesystem is ephemeral, so an
    # ImageField/FileField would lose uploads between deployments.
    profile_photo = models.TextField(blank=True)

    REQUIRED_FIELDS = ["email"]

    def get_full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name, self.suffix]
        return " ".join(part for part in parts if part).strip()

    @property
    def is_parent(self):
        return self.role == self.Role.PARENT

    @property
    def is_staff_role(self):
        return self.role in (self.Role.STAFF, self.Role.ADMIN)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"
