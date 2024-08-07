from rest_framework.decorators import action

from apps.platform_management.models import Administrator
from apps.platform_management.serialiers.administrator import (
    AdministratorListSerializer,
    AdministratorCreateSerializer,
    AdministratorUpdateSerializer,
    AdministratorBatchImportSerializer,
)
from common.utils.drf.response import Response
from common.utils.excel_parser.mapping import ADMINISTRATOR_EXCEL_MAPPING
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission


class AdministratorModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    default_serializer_class = AdministratorUpdateSerializer
    queryset = Administrator.objects.all()
    enable_batch_import = True
    batch_import_serializer = AdministratorBatchImportSerializer
    batch_import_mapping = ADMINISTRATOR_EXCEL_MAPPING
    fuzzy_filter_fields = [
        "username",
        "email",
        "phone",
        "affiliated_manage_company_name",
        "role",
    ]
    filter_condition_mapping = {
        "管理员名称": "name",
        "邮箱": "email",
        "手机": "phone",
        "所属公司": "affiliated_manage_company_name",
        "权限角色": "role",
    }
    filter_condition_enum_list = ["role"]
    ACTION_MAP = {
        "list": AdministratorListSerializer,
        "create": AdministratorCreateSerializer,
    }

    @action(methods=["GET"], detail=False)
    def role_choices(self, request, *args, **kwargs):
        return Response(
            {
                "choices": [
                    {"id": choice.value, "name": choice.label}  # noqa
                    for choice in Administrator.Role
                ],
                "role_tooltips": """平台管理员：有系统全局的权限
    鸿雪公司管理员：有鸿雪公司对应授课空间的权限（可管理对应的客户授课）
    合作伙伴管理员：有合作伙伴公司对应授课空间的权限（可管理对应的客户授课）""",
            }
        )
