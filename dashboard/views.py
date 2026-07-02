from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required, staff_or_admin_required
from accounts.forms import StaffAccountForm
from dashboard.forms import AttendanceForm, ChildForm, GuardianProfileForm, HealthRecordForm
from enrollment.models import Attendance, Child, GuardianProfile, HealthRecord

User = get_user_model()


@staff_or_admin_required
def home(request):
    now = timezone.localtime()
    today = now.date()

    active_count = Child.objects.filter(status=Child.Status.ENROLLED).count()
    total_children = Child.objects.count()
    present_today = Attendance.objects.filter(date=today, status=Attendance.Status.PRESENT).count()
    attendance_rate = round((present_today / active_count) * 100) if active_count else None

    days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    weekly_labels = [day.strftime("%a") for day in days]
    weekly_present = []
    weekly_absent = []
    for day in days:
        day_records = Attendance.objects.filter(date=day)
        weekly_present.append(day_records.filter(status=Attendance.Status.PRESENT).count())
        weekly_absent.append(day_records.filter(status=Attendance.Status.ABSENT).count())

    if now.hour < 12:
        greeting = "morning"
    elif now.hour < 17:
        greeting = "afternoon"
    else:
        greeting = "evening"

    context = {
        "greeting": greeting,
        "active_count": active_count,
        "total_children": total_children,
        "present_today": present_today,
        "attendance_rate": attendance_rate,
        "weekly_labels": weekly_labels,
        "weekly_present": weekly_present,
        "weekly_absent": weekly_absent,
    }
    return render(request, "dashboard/home.html", context)


@staff_or_admin_required
def children_list(request):
    if request.method == "POST":
        form = ChildForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Child added successfully.")
            return redirect("dashboard:children_list")
    else:
        form = ChildForm()
    children = Child.objects.select_related("guardian__user").all()
    return render(request, "dashboard/children_list.html", {"children": children, "form": form})


@staff_or_admin_required
def child_edit(request, pk):
    child = get_object_or_404(Child, pk=pk)
    if request.method == "POST":
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, "Child updated successfully.")
            return redirect("dashboard:children_list")
    else:
        form = ChildForm(instance=child)
    return render(request, "dashboard/child_edit.html", {"form": form, "child": child})


@staff_or_admin_required
@require_POST
def child_delete(request, pk):
    child = get_object_or_404(Child, pk=pk)
    child.delete()
    messages.success(request, "Child removed successfully.")
    return redirect("dashboard:children_list")


@staff_or_admin_required
def guardians_list(request):
    if request.method == "POST":
        form = GuardianProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Guardian profile added successfully.")
            return redirect("dashboard:guardians_list")
    else:
        form = GuardianProfileForm()
    guardians = GuardianProfile.objects.select_related("user").all()
    return render(request, "dashboard/guardians_list.html", {"guardians": guardians, "form": form})


@staff_or_admin_required
def guardian_edit(request, pk):
    guardian = get_object_or_404(GuardianProfile, pk=pk)
    if request.method == "POST":
        form = GuardianProfileForm(request.POST, instance=guardian)
        if form.is_valid():
            form.save()
            messages.success(request, "Guardian profile updated successfully.")
            return redirect("dashboard:guardians_list")
    else:
        form = GuardianProfileForm(instance=guardian)
    return render(request, "dashboard/guardian_edit.html", {"form": form, "guardian": guardian})


@staff_or_admin_required
@require_POST
def guardian_delete(request, pk):
    guardian = get_object_or_404(GuardianProfile, pk=pk)
    guardian.delete()
    messages.success(request, "Guardian profile removed successfully.")
    return redirect("dashboard:guardians_list")


@staff_or_admin_required
def health_records_list(request):
    if request.method == "POST":
        form = HealthRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            messages.success(request, "Health record added successfully.")
            return redirect("dashboard:health_records_list")
    else:
        form = HealthRecordForm()
    records = HealthRecord.objects.select_related("child", "recorded_by").all()
    return render(
        request, "dashboard/health_records_list.html", {"records": records, "form": form}
    )


@staff_or_admin_required
def health_record_edit(request, pk):
    record = get_object_or_404(HealthRecord, pk=pk)
    if request.method == "POST":
        form = HealthRecordForm(request.POST, instance=record)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.recorded_by = request.user
            updated.save()
            messages.success(request, "Health record updated successfully.")
            return redirect("dashboard:health_records_list")
    else:
        form = HealthRecordForm(instance=record)
    return render(request, "dashboard/health_record_edit.html", {"form": form, "record": record})


@staff_or_admin_required
@require_POST
def health_record_delete(request, pk):
    record = get_object_or_404(HealthRecord, pk=pk)
    record.delete()
    messages.success(request, "Health record removed successfully.")
    return redirect("dashboard:health_records_list")


@staff_or_admin_required
def attendance_list(request):
    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance recorded successfully.")
            return redirect("dashboard:attendance_list")
    else:
        form = AttendanceForm()
    records = Attendance.objects.select_related("child").all()
    context = {
        "records": records,
        "form": form,
        "present_count": records.filter(status=Attendance.Status.PRESENT).count(),
        "absent_count": records.filter(status=Attendance.Status.ABSENT).count(),
        "total_count": records.count(),
    }
    return render(request, "dashboard/attendance_list.html", context)


@staff_or_admin_required
def attendance_edit(request, pk):
    record = get_object_or_404(Attendance, pk=pk)
    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance updated successfully.")
            return redirect("dashboard:attendance_list")
    else:
        form = AttendanceForm(instance=record)
    return render(request, "dashboard/attendance_edit.html", {"form": form, "record": record})


@staff_or_admin_required
@require_POST
def attendance_delete(request, pk):
    record = get_object_or_404(Attendance, pk=pk)
    record.delete()
    messages.success(request, "Attendance record removed successfully.")
    return redirect("dashboard:attendance_list")


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
