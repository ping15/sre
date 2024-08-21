from rest_framework.decorators import action

from apps.platform_management.filters.administrator import \
    AdministratorFilterClass
from apps.platform_management.models import Administrator
from apps.platform_management.serialiers.administrator import (
    AdministratorBatchImportSerializer, AdministratorCreateSerializer,
    AdministratorListSerializer, AdministratorUpdateSerializer)
from common.utils import global_constants
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission
from common.utils.drf.response import Response
from common.utils.excel_parser.mapping import ADMINISTRATOR_EXCEL_MAPPING


class AdministratorModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    serializer_class = AdministratorUpdateSerializer
    queryset = Administrator.objects.all()
    enable_batch_import = True
    batch_import_template_path = (
        "common/utils/excel_parser/templates/administrator_template.xlsx"
    )
    batch_import_serializer = AdministratorBatchImportSerializer
    batch_import_mapping = ADMINISTRATOR_EXCEL_MAPPING
    filter_class = AdministratorFilterClass
    ACTION_MAP = {
        "list": AdministratorListSerializer,
        "create": AdministratorCreateSerializer,
    }

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "username", "name": "管理员名称", "children": []},
                {"id": "email", "name": "邮箱", "children": []},
                {"id": "phone", "name": "手机", "children": []},
                {
                    "id": "affiliated_manage_company_name",
                    "name": "所属公司",
                    "children": [],
                },
                {
                    "id": "role",
                    "name": "权限角色",
                    "children": [
                        {"id": value, "name": label}
                        for value, label in Administrator.Role.choices
                    ],
                },
            ]
        )

    @action(methods=["GET"], detail=False)
    def role_choices(self, request, *args, **kwargs):
        return Response(
            {
                "choices": [
                    {"id": choice.value, "name": choice.label}  # noqa
                    for choice in Administrator.Role
                ],
                "role_tooltips": global_constants.ROLE_TOOLTIPS
            }
        )
