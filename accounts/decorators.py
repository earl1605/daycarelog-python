from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def staff_or_admin_required(view_func):
    """Restrict a view to authenticated STAFF or ADMIN users."""

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff_role:
            raise PermissionDenied("You do not have access to this page.")
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Restrict a view to authenticated ADMIN users only."""

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin_role:
            raise PermissionDenied("You do not have access to this page.")
        return view_func(request, *args, **kwargs)

    return wrapper
