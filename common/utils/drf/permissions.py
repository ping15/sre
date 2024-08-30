from rest_framework.permissions import BasePermission

from apps.platform_management.models import Administrator
from common.utils import global_constants


class SuperAdministratorPermission(BasePermission):
    """超级管理员权限"""

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == Administrator.Role.SUPER_MANAGER.value:
            return True
        return False


class ManageCompanyAdministratorPermission(BasePermission):
    """管理公司管理员权限"""

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role in [
            Administrator.Role.PARTNER_MANAGER.value,
            Administrator.Role.COMPANY_MANAGER.value,
        ]:
            return True

        return False


class InstructorPermission(BasePermission):
    """讲师权限"""

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == global_constants.Role.INSTRUCTOR:
            return True

        return False


class StudentPermission(BasePermission):
    """学员权限"""

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == global_constants.Role.CLIENT_STUDENT:
            return True

        return False
