from apps.platform_management.models import ManageCompany, ClientCompany
from apps.platform_management.serialiers.management_company import (
    ManagementCompanyListSerializer,
    ManagementCompanyCreateSerializer,
    ManagementCompanyUpdateSerializer,
)
from apps.teaching_space.models import TrainingClass
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission


class ManagementCompanyModelViewSet(ModelViewSet):
    """管理公司"""

    permission_classes = [SuperAdministratorPermission]
    queryset = ManageCompany.objects.all()
    default_serializer_class = ManagementCompanyCreateSerializer
    fuzzy_filter_fields = ["name", "email"]
    filter_condition_mapping = {
        "公司名称": "name",
        "联系邮箱": "email",
    }
    ACTION_MAP = {
        "list": ManagementCompanyListSerializer,
        "create": ManagementCompanyCreateSerializer,
        "update": ManagementCompanyUpdateSerializer,
        "partial_update": ManagementCompanyUpdateSerializer,
    }

    def update(self, request, *args, **kwargs):
        validated_data = self.validated_data
        if "name" in validated_data:
            origin_manage_company = self.get_object()
            ClientCompany.objects.filter(
                affiliated_manage_company_name=origin_manage_company.name
            ).update(affiliated_manage_company_name=validated_data["name"])
        return super().update(request, *args, **kwargs)

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
