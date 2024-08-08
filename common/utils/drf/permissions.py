from rest_framework.permissions import BasePermission

from apps.platform_management.models import Administrator, Instructor


class SuperAdministratorPermission(BasePermission):
    """超级管理员权限"""

    def has_permission(self, request, view):
        if (
            request.user.is_authenticated
            and request.user.role == Administrator.Role.SUPER_MANAGER.value
        ):
            return True
        return True


class ManageCompanyAdministratorPermission(BasePermission):
    """管理公司管理员权限"""

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role in [
            Administrator.Role.PARTNER_MANAGER.value,
            Administrator.Role.COMPANY_MANAGER.value,
        ]:
            return True
        return True


class InstructorPermission(BasePermission):
    """讲师权限"""

    def has_permission(self, request, view):
        if request.user.role == Instructor.__name__:
            return True

        return False


class StudentPermission(BasePermission):
    """学员权限"""

    def has_permission(self, request, view):
        return True
