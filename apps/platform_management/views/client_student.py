from typing import List

from django.db.models import QuerySet, Count
from django.db.models.functions import TruncDate
from rest_framework.decorators import action

from apps.platform_management.filters.client_student import ClientStudentFilterClass
from apps.platform_management.models import (
    ClientStudent,
    ManageCompany,
    Administrator,
    ClientCompany,
)
from common.utils.drf.response import Response
from common.utils.excel_parser.mapping import CLIENT_STUDENT_EXCEL_MAPPING
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    SuperAdministratorPermission,
    ManageCompanyAdministratorPermission,
)
from apps.platform_management.serialiers.client_student import (
    ClientStudentListSerializer,
    ClientStudentCreateSerializer,
    ClientStudentRetrieveSerializer,
    ClientStudentQuickSearchSerializer,
    ClientStudentUpdateSerializer,
    ClientStudentBatchImportSerializer,
)


class ClientStudentModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    serializer_class = ClientStudentCreateSerializer
    queryset = ClientStudent.objects.all()
    enable_batch_import = True
    batch_import_template_path = (
        "common/utils/excel_parser/templates/client_student_template.xlsx"
    )
    batch_import_mapping = CLIENT_STUDENT_EXCEL_MAPPING
    batch_import_serializer = ClientStudentBatchImportSerializer
    filter_class = ClientStudentFilterClass
    ACTION_MAP = {
        "list": ClientStudentListSerializer,
        "create": ClientStudentCreateSerializer,
        "update": ClientStudentUpdateSerializer,
        "partial_update": ClientStudentUpdateSerializer,
        "retrieve": ClientStudentRetrieveSerializer,
        "quick_search": ClientStudentQuickSearchSerializer,
    }

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[
            SuperAdministratorPermission | ManageCompanyAdministratorPermission
        ],
    )
    def quick_search(self, request, *args, **kwargs):
        if request.user.role == Administrator.Role.SUPER_MANAGER.value:
            manage_companies: QuerySet["ManageCompany"] = ManageCompany.objects.all()
        else:
            manage_companies: List["ManageCompany"] = [
                request.user.affiliated_manage_company
            ]

        return Response(
            [
                {
                    "id": manage_company.id,
                    "name": manage_company.name,
                    "children": [
                        {
                            "id": client_company.id,
                            "name": client_company.name,
                        }
                        for client_company in manage_company.client_companies
                    ],
                }
                for manage_company in manage_companies
            ]
        )

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "name", "name": "学员名称", "children": []},
                {
                    "id": "affiliated_client_company_name",
                    "name": "所属客户公司",
                    "children": [],
                },
                {
                    "id": "affiliated_manage_company_name",
                    "name": "负责的管理公司",
                    "children": [],
                },
                {"id": "email", "name": "邮箱", "children": []},
                {"id": "phone", "name": "手机", "children": []},
                {"id": "phone", "name": "哈哈哈", "children": []},
            ]
        )

    @action(methods=["GET"], detail=False)
    def statistic(self, request, *args, **kwargs):
        # 聚合 ClientCompany 按创建日期统计数量
        company_stats = (
            ClientCompany.objects.values("created_date")
            .annotate(count=Count("id"))
            .order_by("created_date")
        )

        # 聚合 ClientStudent 按创建日期统计数量
        student_stats = (
            ClientStudent.objects.values("created_date")
            .annotate(count=Count("id"))
            .order_by("created_date")
        )

        return Response(
            Response(
                {
                    "client_students": [
                        {"date": stat["created_date"], "count": stat["count"]}
                        for stat in company_stats
                    ],
                    "client_companies": [
                        {"date": stat["created_date"], "count": stat["count"]}
                        for stat in student_stats
                    ],
                }
            )
        )
