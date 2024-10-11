from django.db import transaction
from rest_framework.decorators import action

from apps.platform_management.filters.management_company import (
    ManagementCompanyFilterClass,
)
from apps.platform_management.models import ManageCompany
from apps.platform_management.serialiers.management_company import (
    ManagementCompanyCreateSerializer,
    ManagementCompanyListSerializer,
    ManagementCompanyUpdateSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission
from common.utils.drf.response import Response


class ManagementCompanyModelViewSet(ModelViewSet):
    """管理公司"""

    permission_classes = [SuperAdministratorPermission]
    queryset = ManageCompany.objects.all()
    serializer_class = ManagementCompanyCreateSerializer
    filter_class = ManagementCompanyFilterClass
    ACTION_MAP = {
        "list": ManagementCompanyListSerializer,
        "create": ManagementCompanyCreateSerializer,
        "update": ManagementCompanyUpdateSerializer,
    }

    def update(self, request, *args, **kwargs):
        manage_company: ManageCompany = self.get_object()

        with transaction.atomic():
            response = super().update(request, *args, **kwargs)
            if "name" in self.request.data:
                ManageCompany.sync_name(manage_company.name, self.request.data["name"])
        return response

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
