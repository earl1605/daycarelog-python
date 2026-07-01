from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PARENT = "PARENT", "Parent/Guardian"
        STAFF = "STAFF", "Staff"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PARENT)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=20, blank=True)

    REQUIRED_FIELDS = ["email"]

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
