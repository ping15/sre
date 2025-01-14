from django.db.models import QuerySet
from rest_framework.decorators import action

from apps.platform_management.filters.management_company import (
    ManagementCompanyFilterClass,
)
from apps.platform_management.models import Administrator, ManageCompany
from apps.platform_management.serialiers.management_company import (
    ManagementCompanyCreateSerializer,
    ManagementCompanyListSerializer,
    ManagementCompanyRetrieveSerializer,
    ManagementCompanyUpdateSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    ManageCompanyAdministratorPermission,
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response


class ManagementCompanyModelViewSet(ModelViewSet):
    """管理公司"""

    permission_classes = [SuperAdministratorPermission]
    queryset = ManageCompany.objects.all()
    serializer_class = ManagementCompanyCreateSerializer
    filter_class = ManagementCompanyFilterClass
    ACTION_MAP = {
        "list": ManagementCompanyListSerializer,
        "retrieve": ManagementCompanyRetrieveSerializer,
        "create": ManagementCompanyCreateSerializer,
        "update": ManagementCompanyUpdateSerializer,
        "partial_update": ManagementCompanyUpdateSerializer,
    }
    PERMISSION_MAP = {
        "retrieve": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
        "update": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
        "partial_update": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
    }

    def get_queryset(self):
        queryset: QuerySet[ManageCompany] = super().get_queryset()

        user: Administrator = self.request.user
        if not user.is_super_administrator:
            return queryset.filter(name=user.affiliated_manage_company_name)

        return queryset

    def destroy(self, request, *args, **kwargs):
        manage_company: ManageCompany = self.get_object()
        if manage_company.type == ManageCompany.Type.DEFAULT:
            return Response(result=False, err_msg="默认公司不可删除")

        return super().destroy(request, *args, **kwargs)

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "name", "name": "公司名称", "children": []},
                {"id": "email", "name": "联系邮箱", "children": []},
            ]
        )

    @action(methods=["GET"], detail=False)
    def choices(self, request, *args, **kwargs):
        return Response([
            {
                "id": manage_company.id,
                "name": manage_company.name,
            }
            for manage_company in self.get_queryset()
        ])
