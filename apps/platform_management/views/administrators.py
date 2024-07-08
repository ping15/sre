from rest_framework.viewsets import ModelViewSet

from apps.platform_management.models import Administrator
from apps.platform_management.serialiers.administrators import (
    AdministratorListSerializer,
    AdministratorCreateSerializer
)
from common.permissions import SuperAdministratorPermission


class AdministratorModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    serializer_class = AdministratorListSerializer
    queryset = Administrator.objects.all()

    ACTION_MAP = {
        "list": AdministratorListSerializer,
        "create": AdministratorCreateSerializer,
    }

    def get_serializer_class(self):
        return self.ACTION_MAP.get(self.action, self.serializer_class)  # noqa
