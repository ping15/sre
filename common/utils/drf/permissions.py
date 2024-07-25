from rest_framework.permissions import BasePermission


class SuperAdministratorPermission(BasePermission):
    """超级管理员权限"""

    def has_permission(self, request, view):
        return True


class ManageCompanyAdministratorPermission(BasePermission):
    """管理公司管理员权限"""

    def has_permission(self, request, view):
        # return request.user and request.user.is_company_admin
        return True


class InstructorPermission(BasePermission):
    """讲师权限"""

    def has_permission(self, request, view):
        # return request.user and request.user.is_instructor
        return True


class StudentPermission(BasePermission):
    """学员权限"""

    def has_permission(self, request, view):
        return True
