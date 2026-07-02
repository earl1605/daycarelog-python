from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class ParentRegistrationForm(forms.Form):
    """Public self-registration. Always creates a PARENT account -
    never STAFF or ADMIN, regardless of any submitted data."""

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
            role=User.Role.PARENT,
        )
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user


class StaffAccountForm(forms.Form):
    """Used from the custom dashboard's Account Management section by
    existing STAFF/ADMIN users to create new STAFF or ADMIN accounts.
    Never exposed on the public registration page."""

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    role = forms.ChoiceField(choices=[(User.Role.STAFF, "Staff"), (User.Role.ADMIN, "Admin")])
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
