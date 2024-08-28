from rest_framework.decorators import action

from apps.platform_management.filters.client_company import \
    ClientCompanyFilterClass
from apps.platform_management.models import ClientCompany
from apps.platform_management.serialiers.client_company import (
    ClientCompanyCreateSerializer, ClientCompanyListSerializer,
    ClientCompanyRetrieveSerializer)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission
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
        "update": ClientCompanyCreateSerializer,
        # "partial_update": ClientCompanyCreateSerializer,
    }

    def list(self, request, *args, **kwargs):
        # user: Administrator = request.user
        #
        # # 非超级管理员只能看到自己所属管理公司下面的客户公司
        # if user.role in [Administrator.Role.PARTNER_MANAGER, Administrator.Role.COMPANY_MANAGER]:
        #     self.queryset = self.get_queryset().filter(
        #         affiliated_manage_company_name=user.affiliated_manage_company_name)

        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if "name" in self.request.data:
            ClientCompany.sync_name(self.get_object().name, self.request.data["name"])
        return super().update(request, *args, **kwargs)

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "name", "name": "客户公司名称", "children": []},
                {"id": "contact_email", "name": "联系邮箱", "children": []},
                {
                    "id": "affiliated_manage_company_name",
                    "name": "管理公司名称",
                    "children": [],
                },
            ]
        )
