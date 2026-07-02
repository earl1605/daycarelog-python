from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from enrollment.models import Attendance, Child, GuardianProfile, HealthRecord

User = get_user_model()


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ["guardian", "first_name", "last_name", "date_of_birth", "sex", "status"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["guardian"].queryset = GuardianProfile.objects.select_related(
            "user"
        ).order_by("user__first_name", "user__last_name")


class GuardianProfileForm(forms.ModelForm):
    class Meta:
        model = GuardianProfile
        fields = ["user", "address", "relationship_to_child"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available = Q(role=User.Role.PARENT, guardian_profile__isnull=True)
        if self.instance.pk:
            available |= Q(pk=self.instance.user_id)
        self.fields["user"].queryset = User.objects.filter(available).order_by(
            "first_name", "last_name"
        )


class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = ["child", "record_date", "height_cm", "weight_kg", "temperature_c", "allergies", "notes"]
        widgets = {
            "record_date": forms.DateInput(attrs={"type": "date"}),
            "allergies": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["child"].queryset = Child.objects.order_by("first_name", "last_name")


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["child", "date", "status", "remarks"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["child"].queryset = Child.objects.order_by("first_name", "last_name")
