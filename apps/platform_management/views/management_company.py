from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.platform_management.models import ManageCompany
from apps.platform_management.serialiers.management_company import (
    ManagementCompanySerializer,
)
from common.utils.permissions import SuperAdministratorPermission


class ManagementCompanyModelViewSet(ModelViewSet):
    """管理公司"""

    permission_classes = [SuperAdministratorPermission]
    queryset = ManageCompany.objects.all()
    serializer_class = ManagementCompanySerializer

    @action(methods=["GET"], detail=False)
    def names(self, request, *args, **kwargs):
        return Response(list(self.queryset.values_list("name", flat=True)))

    # def list(self, request, *args, **kwargs):
    #     mock_data = [
    #         {
    #             "name": "鸿雪公司",
    #             "type": "默认公司",
    #             "email": "123@qq.com",
    #         },
    #         {
    #             "name": "合作伙伴公司A",
    #             "type": "合作伙伴",
    #             "email": "123@qq.com",
    #         },
    #         {
    #             "name": "合作伙伴公司B",
    #             "type": "合作伙伴",
    #             "email": "123@qq.com",
    #         },
    #     ]
    #     return Response({
    #         "count": 3,
    #         "next": None,
    #         "previous": None,
    #         "results": mock_data,
    #     })
