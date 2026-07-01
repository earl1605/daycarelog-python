from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from enrollment.models import Attendance, Child, GuardianProfile, HealthRecord

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "middle_name", "suffix", "full_name",
            "contact_number", "role", "role_display",
        ]
        read_only_fields = ["id", "role", "role_display", "full_name"]


class RegisterSerializer(serializers.Serializer):
    """Public self-registration. Always creates a PARENT account -
    never STAFF or ADMIN, regardless of any submitted data."""

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    middle_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    suffix = serializers.ChoiceField(choices=User.Suffix.choices, required=False, allow_blank=True)
    email = serializers.EmailField()
    contact_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        email = validated_data["email"]
        user = User(
            username=email,
            email=email,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            middle_name=validated_data.get("middle_name", ""),
            suffix=validated_data.get("suffix", ""),
            contact_number=validated_data.get("contact_number", ""),
            role=User.Role.PARENT,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class StaffAccountSerializer(serializers.Serializer):
    """Used by an existing STAFF/ADMIN (via the admin-only API) to create new
    STAFF or ADMIN accounts. Never exposed on the public registration endpoint."""

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=[(User.Role.STAFF, "Staff"), (User.Role.ADMIN, "Admin")])
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        user = User(
            username=email,
            email=email,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role=validated_data["role"],
            is_staff=validated_data["role"] == User.Role.ADMIN,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["email"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        attrs["user"] = user
        return attrs


class GuardianProfileSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = GuardianProfile
        fields = ["id", "user", "user_full_name", "user_email", "address", "relationship_to_child"]


class ChildSerializer(serializers.ModelSerializer):
    sex_display = serializers.CharField(source="get_sex_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    guardian_name = serializers.CharField(source="guardian.user.get_full_name", read_only=True)

    class Meta:
        model = Child
        fields = [
            "id", "guardian", "guardian_name", "first_name", "last_name",
            "date_of_birth", "sex", "sex_display", "status", "status_display",
            "enrollment_date",
        ]
        read_only_fields = ["enrollment_date"]


class HealthRecordSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.__str__", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = HealthRecord
        fields = [
            "id", "child", "child_name", "record_date", "height_cm", "weight_kg",
            "temperature_c", "allergies", "notes", "recorded_by", "recorded_by_name",
        ]
        read_only_fields = ["recorded_by"]


class AttendanceSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.__str__", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "child", "child_name", "date", "status", "status_display", "remarks"]
