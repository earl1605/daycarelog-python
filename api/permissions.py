from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffOrAdmin(BasePermission):
    """Allows access to authenticated STAFF or ADMIN users only."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_staff_role)


class IsAdminRole(BasePermission):
    """Allows access to authenticated ADMIN users only."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_admin_role)


class IsStaffOrAdminOrReadOnlyOwnChild(BasePermission):
    """Any authenticated user may read (queryset scopes parents to their own
    children); only STAFF/ADMIN may create, update, or delete."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.is_staff_role
