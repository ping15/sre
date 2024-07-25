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
    ACTION_MAP = {
        "list": AdministratorListSerializer,
        "create": AdministratorCreateSerializer,
    }
