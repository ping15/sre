from django.db.models import QuerySet
from rest_framework.decorators import action

from apps.platform_management.filters.client_company import ClientCompanyFilterClass
from apps.platform_management.models import Administrator, ClientCompany
from apps.platform_management.serialiers.client_company import (
    ClientCompanyCreateSerializer,
    ClientCompanyListSerializer,
    ClientCompanyRetrieveSerializer,
    ClientCompanyUpdateSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    ManageCompanyAdministratorPermission,
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response


class ClientCompanyModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    serializer_class = ClientCompanyListSerializer
    queryset = ClientCompany.objects.all()
    filter_class = ClientCompanyFilterClass
    ACTION_MAP = {
        "list": ClientCompanyListSerializer,
        "create": ClientCompanyCreateSerializer,
        "retrieve": ClientCompanyRetrieveSerializer,
        "update": ClientCompanyUpdateSerializer,
    }
    PERMISSION_MAP = {
        "list": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
        "create": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
        "retrieve": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
        "update": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
        "destroy": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
        "choices": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
    }

    def get_queryset(self):
        queryset: QuerySet["ClientCompany"] = super().get_queryset()

        # 非超级管理员只能看到自己所属管理公司下面的客户公司
        user: Administrator = self.request.user
        if not user.is_super_administrator:
            queryset = queryset.filter(affiliated_manage_company_name=user.affiliated_manage_company_name)

        return queryset

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "name", "name": "客户公司名称", "children": []},
                {"id": "contact_email", "name": "联系邮箱", "children": []},
                {"id": "affiliated_manage_company_name", "name": "管理公司名称", "children": []},
            ]
        )

    @action(methods=["GET"], detail=False)
    def choices(self, request, *args, **kwargs):
        user: Administrator = request.user

        if user.is_super_administrator:
            client_companies: QuerySet["ClientCompany"] = ClientCompany.objects.all()
        else:
            client_companies: QuerySet["ClientCompany"] = user.affiliated_manage_company.client_companies

        return Response([
            {"id": client_company.id, "name": client_company.name}
            for client_company in client_companies
        ])
