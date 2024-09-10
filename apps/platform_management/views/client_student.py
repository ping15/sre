from typing import List

from dateutil.relativedelta import relativedelta
from django.db.models import Count, QuerySet
from django.db.models.functions import TruncMonth
from rest_framework.decorators import action

from apps.platform_management.filters.client_student import ClientStudentFilterClass
from apps.platform_management.models import (
    Administrator,
    ClientCompany,
    ClientStudent,
    ManageCompany,
)
from apps.platform_management.serialiers.client_student import (
    ClientStudentBatchImportSerializer,
    ClientStudentCreateSerializer,
    ClientStudentFilterConditionSerializer,
    ClientStudentListSerializer,
    ClientStudentQuickSearchSerializer,
    ClientStudentRetrieveSerializer,
    ClientStudentStatisticSerializer,
    ClientStudentUpdateSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    ManageCompanyAdministratorPermission,
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response
from common.utils.excel_parser.mapping import CLIENT_STUDENT_EXCEL_MAPPING
from common.utils.global_constants import AppModule


class ClientStudentModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission | ManageCompanyAdministratorPermission]
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

    def get_queryset(self) -> QuerySet["ClientStudent"]:
        queryset: QuerySet["ClientStudent"] = super().get_queryset()
        user: Administrator = self.request.user

        # 非超级管理员只能看到自己所属管理公司下面的所有学员
        if user.role != Administrator.Role.SUPER_MANAGER:
            queryset: QuerySet["ClientStudent"] = user.affiliated_manage_company.students

        return queryset

    @action(methods=["GET"], detail=False)
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

    @action(methods=["GET"], detail=False)
    def choices(self, request, *args, **kwargs):
        return Response([
            {
                "id": client_student.id,
                "name": client_student.username,
            }
            for client_student in self.get_queryset()
        ])

    @action(methods=["GET"], detail=False)
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
                    {"id": "education", "name": "学历", "children": [
                        {"id": choice.value, "name": choice.label}  # noqa
                        for choice in ClientStudent.Education
                    ]},
                    {"id": "phone", "name": "电话", "children": []},
                    {"id": "email", "name": "邮箱", "children": []},
                    {"id": "department", "name": "部门", "children": []},
                    {"id": "position", "name": "职位", "children": []},
                ]
            )

        return Response([])

    @action(methods=["GET"], detail=False)
    def statistic_client_companies(self, request, *args, **kwargs):
        validated_data = self.validated_data

        start_date, end_date = validated_data["start_date"], validated_data["end_date"]
        client_company_id = request.query_params.get("affiliated_client_company")

        client_companies: QuerySet["ClientCompany"] = request.user.affiliated_manage_company.client_companies
        if client_company_id:
            try:
                # 查找该客户公司所属的管理公司下面所有客户公司
                client_company: ClientCompany = ClientCompany.objects.get(id=int(client_company_id))
                client_companies = client_company.affiliated_manage_company.client_companies

            except (ValueError, KeyError):
                return Response(result=False, err_msg="无效的客户公司ID")

            except ClientCompany.DoesNotExist:
                return Response(result=False, err_msg="查不到该客户公司")

        return Response(self._handle_statistic(client_companies, start_date, end_date))

    @action(methods=["GET"], detail=False)
    def statistic_client_students(self, request, *args, **kwargs):
        validated_data = self.validated_data

        start_date, end_date = validated_data["start_date"], validated_data["end_date"]

        client_students: QuerySet["ClientStudent"] = self.filter_queryset(self.get_queryset())

        return Response(self._handle_statistic(client_students, start_date, end_date))

    @staticmethod
    def _handle_statistic(queryset, start_date, end_date):
        # 截取日期到月份级别并聚合统计
        company_stats = (
            queryset.filter(created_date__gte=start_date, created_date__lte=end_date)
            .annotate(month=TruncMonth("created_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        # 构建月份区间列表
        start_month = start_date.replace(day=1)
        end_month = end_date.replace(day=1)
        months = []
        while start_month <= end_month:
            months.append(start_month)
            start_month += relativedelta(months=1)

        # 构建返回数据
        return {
            "total": sum(stat["count"] for stat in company_stats),
            "data": [
                {
                    "date": month.strftime("%Y-%m"),
                    "count": next((stat["count"] for stat in company_stats if stat["month"] == month), 0)
                }
                for month in months
            ],
        }
