from apps.platform_management.models import Administrator
from apps.platform_management.serialiers.administrator import (
    AdministratorListSerializer,
    AdministratorCreateSerializer,
)
from common.utils.excel_parser.mapping import ADMINISTRATOR_EXCEL_MAPPING
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission


class AdministratorModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    default_serializer_class = AdministratorCreateSerializer
    queryset = Administrator.objects.all()
    enable_batch_import = True
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
