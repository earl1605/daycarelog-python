from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q

from accounts.models import contact_number_validator
from accounts.utils import generate_temp_password
from enrollment.immunizations import EPI_SCHEDULE
from enrollment.models import Attendance, Child, GuardianProfile, HealthRecord, Immunization

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


class GuardianAccountCreateForm(forms.Form):
    """Used by STAFF/ADMIN on the Guardians page to create a brand-new
    Parent/Guardian account together with its GuardianProfile in one step -
    a Parent/Guardian account can never come from public self-registration,
    since claiming a specific child needs staff verification. A temporary
    password is generated and returned by save() for staff to share once."""

    first_name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "capitalize-name"})
    )
    last_name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "capitalize-name"})
    )
    middle_name = forms.CharField(
        max_length=150, required=False, widget=forms.TextInput(attrs={"class": "capitalize-name"})
    )
    suffix = forms.ChoiceField(choices=User.Suffix.choices, required=False)
    email = forms.EmailField()
    contact_number = forms.CharField(
        max_length=20, required=False, validators=[contact_number_validator]
    )
    address = forms.CharField(max_length=255, required=False)
    relationship_to_child = forms.CharField(max_length=50, required=True)

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def save(self):
        email = self.cleaned_data["email"]
        temp_password = generate_temp_password()
        user = User(
            username=email,
            email=email,
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            middle_name=self.cleaned_data.get("middle_name", ""),
            suffix=self.cleaned_data.get("suffix", ""),
            contact_number=self.cleaned_data.get("contact_number", ""),
            role=User.Role.PARENT,
        )
        user.set_password(temp_password)
        user.save()
        guardian_profile = GuardianProfile.objects.create(
            user=user,
            address=self.cleaned_data.get("address", ""),
            relationship_to_child=self.cleaned_data.get("relationship_to_child", ""),
        )
        return guardian_profile, temp_password


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


class ImmunizationForm(forms.ModelForm):
    vaccine_name = forms.ChoiceField(choices=[(v["name"], v["name"]) for v in EPI_SCHEDULE])

    class Meta:
        model = Immunization
        fields = ["child", "vaccine_name", "dose_number", "date_given", "administered_by", "notes"]
        widgets = {
            "date_given": forms.DateInput(attrs={"type": "date"}),
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
            "date": forms.DateInput(attrs={"type": "date", "class": "weekday-only-date"}),
        }

    def clean_date(self):
        value = self.cleaned_data["date"]
        if value.weekday() >= 5:
            raise forms.ValidationError(
                "Attendance can only be recorded for weekdays (Monday–Friday)."
            )
        return value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["child"].queryset = Child.objects.order_by("first_name", "last_name")
