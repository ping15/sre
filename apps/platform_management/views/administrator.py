from apps.platform_management.models import Administrator
from apps.platform_management.serialiers.administrator import (
    AdministratorListSerializer,
    AdministratorCreateSerializer,
)
from common.utils.excel_parser.mapping import ADMINISTRATOR_EXCEL_MAPPING
from common.utils.modelviewset import ModelViewSet
from common.utils.permissions import SuperAdministratorPermission


class AdministratorModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    serializer_class = AdministratorListSerializer
    queryset = Administrator.objects.all()
    enable_batch_import = True
    batch_import_mapping = ADMINISTRATOR_EXCEL_MAPPING
    batch_import_serializer = AdministratorCreateSerializer
    ACTION_MAP = {
        "list": AdministratorListSerializer,
        "create": AdministratorCreateSerializer,
    }
