from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required, staff_or_admin_required
from accounts.forms import StaffAccountForm
from enrollment.models import Attendance, Child, GuardianProfile, HealthRecord

User = get_user_model()


@staff_or_admin_required
def home(request):
    context = {
        "total_children": Child.objects.count(),
        "enrolled_count": Child.objects.filter(status=Child.Status.ENROLLED).count(),
        "pending_count": Child.objects.filter(status=Child.Status.PENDING).count(),
        "guardian_count": GuardianProfile.objects.count(),
        "recent_health_records": HealthRecord.objects.select_related("child")[:5],
    }
    return render(request, "dashboard/home.html", context)


@staff_or_admin_required
def children_list(request):
    children = Child.objects.select_related("guardian__user").all()
    return render(request, "dashboard/children_list.html", {"children": children})


@staff_or_admin_required
def guardians_list(request):
    guardians = GuardianProfile.objects.select_related("user").all()
    return render(request, "dashboard/guardians_list.html", {"guardians": guardians})


@staff_or_admin_required
def health_records_list(request):
    records = HealthRecord.objects.select_related("child", "recorded_by").all()
    return render(request, "dashboard/health_records_list.html", {"records": records})


@staff_or_admin_required
def attendance_list(request):
    records = Attendance.objects.select_related("child").all()
    return render(request, "dashboard/attendance_list.html", {"records": records})


@admin_required
def account_management(request):
    accounts = User.objects.filter(role__in=[User.Role.STAFF, User.Role.ADMIN])
    if request.method == "POST":
        form = StaffAccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully.")
            return redirect("dashboard:account_management")
    else:
        form = StaffAccountForm()
    return render(
        request, "dashboard/account_management.html", {"accounts": accounts, "form": form}
    )


@login_required
def parent_home(request):
    if request.user.is_staff_role:
        return redirect("dashboard:home")
    guardian_profile = GuardianProfile.objects.filter(user=request.user).first()
    children = Child.objects.filter(guardian=guardian_profile) if guardian_profile else []
    return render(
        request,
        "dashboard/parent_home.html",
        {"guardian_profile": guardian_profile, "children": children},
    )
