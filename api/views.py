from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from enrollment.models import Attendance, Child, GuardianProfile, HealthRecord

from .permissions import IsAdminRole, IsStaffOrAdmin, IsStaffOrAdminOrReadOnlyOwnChild
from .serializers import (
    AttendanceSerializer,
    ChildSerializer,
    GuardianProfileSerializer,
    HealthRecordSerializer,
    LoginSerializer,
    RegisterSerializer,
    StaffAccountSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data}, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=204)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class DashboardStatsView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        return Response({
            "total_children": Child.objects.count(),
            "enrolled_count": Child.objects.filter(status=Child.Status.ENROLLED).count(),
            "pending_count": Child.objects.filter(status=Child.Status.PENDING).count(),
            "guardian_count": GuardianProfile.objects.count(),
        })


class StaffAccountListCreateView(APIView):
    """List and create STAFF/ADMIN accounts (admin only) - the API equivalent
    of the dashboard's Account Management page."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        accounts = User.objects.filter(role__in=[User.Role.STAFF, User.Role.ADMIN])
        return Response(UserSerializer(accounts, many=True).data)

    def post(self, request):
        serializer = StaffAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=201)


class ChildViewSet(viewsets.ModelViewSet):
    serializer_class = ChildSerializer
    permission_classes = [IsStaffOrAdminOrReadOnlyOwnChild]

    def get_queryset(self):
        user = self.request.user
        queryset = Child.objects.select_related("guardian__user")
        if user.is_staff_role:
            return queryset
        return queryset.filter(guardian__user=user)


class GuardianProfileViewSet(viewsets.ModelViewSet):
    queryset = GuardianProfile.objects.select_related("user")
    serializer_class = GuardianProfileSerializer
    permission_classes = [IsStaffOrAdmin]


class HealthRecordViewSet(viewsets.ModelViewSet):
    serializer_class = HealthRecordSerializer
    permission_classes = [IsStaffOrAdminOrReadOnlyOwnChild]

    def get_queryset(self):
        user = self.request.user
        queryset = HealthRecord.objects.select_related("child", "recorded_by")
        if user.is_staff_role:
            return queryset
        return queryset.filter(child__guardian__user=user)

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsStaffOrAdminOrReadOnlyOwnChild]

    def get_queryset(self):
        user = self.request.user
        queryset = Attendance.objects.select_related("child")
        if user.is_staff_role:
            return queryset
        return queryset.filter(child__guardian__user=user)
