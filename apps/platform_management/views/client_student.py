from rest_framework.decorators import action

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
)


class ClientStudentModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    default_serializer_class = ClientStudentCreateSerializer
    queryset = ClientStudent.objects.all()
    enable_batch_import = True
    batch_import_mapping = CLIENT_STUDENT_EXCEL_MAPPING
    fuzzy_filter_fields = [
        "name",
        "affiliated_client_company_name",
        "affiliated_manage_company_name",
        "email",
        "phone",
    ]
    filter_condition_mapping = {
        "学员名称": "name",
        "所属客户公司": "affiliated_client_company_name",
        "负责的管理公司": "affiliated_manage_company_name",
        "邮箱": "email",
        "手机": "phone",
    }
    ACTION_MAP = {
        "list": ClientStudentListSerializer,
        "create": ClientStudentCreateSerializer,
        "retrieve": ClientStudentRetrieveSerializer,
        "quick_search": ClientStudentQuickSearchSerializer,
    }

    @action(methods=["GET"], detail=False)
    def quick_search(self, request, *args, **kwargs):
        return Response(
            self.get_serializer(ManageCompany.objects.all(), many=True).data
        )
