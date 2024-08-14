from rest_framework.decorators import action

from apps.platform_management.filters.client_student import ClientStudentFilterClass
from apps.platform_management.models import ClientStudent, ManageCompany
from common.utils.drf.response import Response
from common.utils.excel_parser.mapping import CLIENT_STUDENT_EXCEL_MAPPING
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission
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
    default_serializer_class = ClientStudentCreateSerializer
    queryset = ClientStudent.objects.all()
    enable_batch_import = True
    batch_import_template_path = (
        "common/utils/excel_parser/templates/client_student_template.xlsx"
    )
    batch_import_mapping = CLIENT_STUDENT_EXCEL_MAPPING
    batch_import_serializer = ClientStudentBatchImportSerializer
    filter_class = ClientStudentFilterClass
    # string_fuzzy_filter_fields = [
    #     "username",
    #     "affiliated_client_company_name",
    #     "affiliated_manage_company_name",
    #     "email",
    #     "phone",
    # ]
    ACTION_MAP = {
        "list": ClientStudentListSerializer,
        "create": ClientStudentCreateSerializer,
        "update": ClientStudentUpdateSerializer,
        "partial_update": ClientStudentUpdateSerializer,
        "retrieve": ClientStudentRetrieveSerializer,
        "quick_search": ClientStudentQuickSearchSerializer,
    }

    @action(methods=["GET"], detail=False)
    def quick_search(self, request, *args, **kwargs):
        return Response(
            [
                {
                    "id": "affiliated_manage_company_name",
                    "name": manage_company.name,
                    "children": [
                        {
                            "id": client_company.id,
                            "name": client_company.name,
                        }
                        for client_company in manage_company.client_companies
                    ],
                }
                for manage_company in ManageCompany.objects.all()
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
            ]
        )
