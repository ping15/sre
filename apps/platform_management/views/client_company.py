from apps.platform_management.models import ClientCompany
from apps.platform_management.serialiers.client_company import (
    ClientCompanyListSerializer,
    ClientCompanyCreateSerializer,
    ClientCompanyRetrieveSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission


class ClientCompanyModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    default_serializer_class = ClientCompanyListSerializer
    queryset = ClientCompany.objects.all()
    ACTION_MAP = {
        "list": ClientCompanyListSerializer,
        "create": ClientCompanyCreateSerializer,
        "retrieve": ClientCompanyRetrieveSerializer,
    }
