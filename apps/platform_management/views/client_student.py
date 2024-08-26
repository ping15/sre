from typing import List

from django.db.models import Count, QuerySet
from rest_framework.decorators import action

from apps.platform_management.filters.client_student import \
    ClientStudentFilterClass
from apps.platform_management.models import (Administrator, ClientCompany,
                                             ClientStudent, ManageCompany)
from apps.platform_management.serialiers.client_student import (
    ClientStudentBatchImportSerializer, ClientStudentCreateSerializer,
    ClientStudentFilterConditionSerializer, ClientStudentListSerializer,
    ClientStudentQuickSearchSerializer, ClientStudentRetrieveSerializer,
    ClientStudentStatisticSerializer, ClientStudentUpdateSerializer)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (ManageCompanyAdministratorPermission,
                                          SuperAdministratorPermission)
from common.utils.drf.response import Response
from common.utils.excel_parser.mapping import CLIENT_STUDENT_EXCEL_MAPPING
from common.utils.global_constants import AppModule


class ClientStudentModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    serializer_class = ClientStudentCreateSerializer
    queryset = ClientStudent.objects.all()
    enable_batch_import = True
    batch_import_template_path = "common/utils/excel_parser/templates/client_student_template.xlsx"
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
        "statistic_client_companies": ClientStudentStatisticSerializer,
        "statistic_client_students": ClientStudentStatisticSerializer,
        "filter_condition": ClientStudentFilterConditionSerializer,
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
            manage_companies: List["ManageCompany"] = [request.user.affiliated_manage_company]

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

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[
            SuperAdministratorPermission | ManageCompanyAdministratorPermission
        ],
    )
    def filter_condition(self, request, *args, **kwargs):
        validated_date = self.validated_data

        if validated_date["module"] == AppModule.PLATFORM_MANAGEMENT.value:
            return Response(
                [
                    {"id": "name", "name": "学员名称", "children": []},
                    {"id": "affiliated_client_company_name", "name": "所属客户公司", "children": []},
                    {"id": "affiliated_manage_company_name", "name": "负责的管理公司", "children": []},
                    {"id": "email", "name": "邮箱", "children": []},
                    {"id": "phone", "name": "手机", "children": []},
                ]
            )

        elif validated_date["module"] == AppModule.TEACHING_SPACE.value:
            return Response(
                [
                    {"id": "username", "name": "学员名称", "children": []},
                    {"id": "sex", "name": "性别", "children": []},
                    {"id": "id_number", "name": "身份证", "children": []},
                    {"id": "education", "name": "学历", "children": []},
                    {"id": "phone", "name": "电话", "children": []},
                    {"id": "email", "name": "邮箱", "children": []},
                    {"id": "department", "name": "部门", "children": []},
                    {"id": "position", "name": "职位", "children": []},
                ]
            )

        return Response([])

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[
            SuperAdministratorPermission | ManageCompanyAdministratorPermission
        ],
    )
    def statistic_client_companies(self, request, *args, **kwargs):
        validated_data = self.validated_data

        # 超级管理员能看到所有客户公司的信息
        # 管理公司管理员只能看到所在管理公司下面所有客户公司的信息
        if request.user.role == Administrator.Role.SUPER_MANAGER.value:
            client_companies: QuerySet["ClientCompany"] = ClientCompany.objects.all()
        else:
            client_companies: QuerySet["ClientCompany"] = request.user.affiliated_manage_company.client_companies

        # 聚合 ClientCompany 按创建日期统计数量
        company_stats = (
            client_companies.filter(
                created_date__gte=validated_data["start_date"],
                created_date__lte=validated_data["end_date"],
            )
            .values("created_date")
            .annotate(count=Count("id"))
            .order_by("created_date")
        )

        return Response(
            {
                "total": sum(stat["count"] for stat in company_stats),
                "data": [
                    {
                        "date": stat["created_date"],
                        "count": stat["count"]
                    }
                    for stat in company_stats
                ],
            }
        )

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[
            SuperAdministratorPermission | ManageCompanyAdministratorPermission
        ],
    )
    def statistic_client_students(self, request, *args, **kwargs):
        validated_data = self.validated_data

        # 超级管理员能看到所有所有学员的信息
        # 管理公司管理员只能看到所在管理公司下面所有学员的信息
        if request.user.role == Administrator.Role.SUPER_MANAGER.value:
            client_students: QuerySet["ClientStudent"] = ClientStudent.objects.all()
        else:
            client_students: QuerySet["ClientStudent"] = request.user.affiliated_manage_company.students

        # 聚合 ClientStudent 按创建日期统计数量
        student_stats = (
            client_students.filter(
                created_date__gte=validated_data["start_date"],
                created_date__lte=validated_data["end_date"],
            )
            .values("created_date")
            .annotate(count=Count("id"))
            .order_by("created_date")
        )

        return Response(
            {
                "total": sum(stat["count"] for stat in student_stats),
                "data": [
                    {
                        "date": stat["created_date"],
                        "count": stat["count"]
                    }
                    for stat in student_stats
                ],
            }
        )
