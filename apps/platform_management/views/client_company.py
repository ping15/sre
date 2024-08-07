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
    fuzzy_filter_fields = ["name", "contact_email", "affiliated_manage_company_name"]
    filter_condition_mapping = {
        "客户公司名称": "name",
        "联系邮箱": "contact_email",
        "管理公司名称": "affiliated_manage_company_name",
    }
    ACTION_MAP = {
        "list": ClientCompanyListSerializer,
        "create": ClientCompanyCreateSerializer,
        "retrieve": ClientCompanyRetrieveSerializer,
        "update": ClientCompanyCreateSerializer,
        "partial_update": ClientCompanyCreateSerializer,
    }
