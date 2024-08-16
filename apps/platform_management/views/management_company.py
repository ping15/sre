from rest_framework.decorators import action

from apps.platform_management.filters.management_company import (
    ManagementCompanyFilterClass,
)
from apps.platform_management.models import ManageCompany, ClientCompany
from apps.platform_management.serialiers.management_company import (
    ManagementCompanyListSerializer,
    ManagementCompanyCreateSerializer,
    ManagementCompanyUpdateSerializer,
    ManagementCompanyPartialUpdateSerializer,
)
from apps.teaching_space.models import TrainingClass
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission
from common.utils.drf.response import Response


class ManagementCompanyModelViewSet(ModelViewSet):
    """管理公司"""

    permission_classes = [SuperAdministratorPermission]
    queryset = ManageCompany.objects.all()
    serializer_class = ManagementCompanyCreateSerializer
    # string_fuzzy_filter_fields = ["name", "email"]
    filter_class = ManagementCompanyFilterClass
    ACTION_MAP = {
        "list": ManagementCompanyListSerializer,
        "create": ManagementCompanyCreateSerializer,
        "update": ManagementCompanyUpdateSerializer,
        "partial_update": ManagementCompanyUpdateSerializer,
    }

    def update(self, request, *args, **kwargs):
        if "name" in self.request.data:
            ManageCompany.sync_name(self.get_object().name, self.request.data["name"])
        return super().update(request, *args, **kwargs)

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "name", "name": "公司名称", "children": []},
                {"id": "email", "name": "联系邮箱", "children": []},
            ]
        )
