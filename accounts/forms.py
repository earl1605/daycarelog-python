from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class PublicRegistrationForm(forms.Form):
    """Public self-registration. Always creates a STAFF account - never ADMIN,
    and never PARENT, regardless of any submitted data. Parent/Guardian
    accounts can only be created by an existing STAFF/ADMIN from the
    Guardians page (see GuardianAccountCreateForm), since a parent claiming
    a specific child needs staff verification, not open self-service."""

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "capitalize-name", "autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "capitalize-name", "autocomplete": "family-name"}),
    )
    middle_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "capitalize-name", "autocomplete": "additional-name"}),
    )
    suffix = forms.ChoiceField(choices=User.Suffix.choices, required=False)
    email = forms.EmailField()
    contact_number = forms.CharField(max_length=20, required=False)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self):
        email = self.cleaned_data["email"]
        user = User(
            username=email,
            email=email,
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            middle_name=self.cleaned_data.get("middle_name", ""),
            suffix=self.cleaned_data.get("suffix", ""),
            contact_number=self.cleaned_data.get("contact_number", ""),
            role=User.Role.STAFF,
        )
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user


class StaffAccountForm(forms.Form):
    """Used from the custom dashboard's Account Management section by
    existing STAFF/ADMIN users to create new STAFF or ADMIN accounts.
    Never exposed on the public registration page."""

    first_name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "capitalize-name"})
    )
    last_name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": "capitalize-name"})
    )
    email = forms.EmailField()
    role = forms.ChoiceField(
        choices=[(User.Role.STAFF, User.Role.STAFF.label), (User.Role.ADMIN, User.Role.ADMIN.label)]
    )
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def save(self):
        email = self.cleaned_data["email"]
        user = User(
            username=email,
            email=email,
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            role=self.cleaned_data["role"],
            is_staff=self.cleaned_data["role"] == User.Role.ADMIN,
        )
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user


class DaycareLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class ProfileForm(forms.ModelForm):
    """Used from the Settings page for a user to edit their own name fields."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "middle_name", "suffix"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "capitalize-name", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"class": "capitalize-name", "autocomplete": "family-name"}),
            "middle_name": forms.TextInput(attrs={"class": "capitalize-name", "autocomplete": "additional-name"}),
        }


class ProfilePhotoForm(forms.ModelForm):
    """Used from the Settings page to update just the profile photo - kept
    separate from ProfileForm so submitting the name fields never risks
    clobbering an existing photo (or vice versa)."""

    class Meta:
        model = User
        fields = ["profile_photo"]
        widgets = {"profile_photo": forms.HiddenInput()}
