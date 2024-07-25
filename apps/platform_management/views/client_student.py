from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.platform_management.models import ClientStudent
from common.utils.excel_parser.mapping import CLIENT_STUDENT_EXCEL_MAPPING
from common.utils.modelviewset import ModelViewSet
from common.utils.permissions import SuperAdministratorPermission
from apps.platform_management.serialiers.client_student import (
    ClientStudentListSerializer,
    ClientStudentCreateSerializer,
    ClientStudentRetrieveSerializer,
)


class ClientStudentModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    default_serializer_class = ClientStudentCreateSerializer
    queryset = ClientStudent.objects.all()
    enable_batch_import = True
    batch_import_mapping = CLIENT_STUDENT_EXCEL_MAPPING
    ACTION_MAP = {
        "list": ClientStudentListSerializer,
        "create": ClientStudentCreateSerializer,
        "retrieve": ClientStudentRetrieveSerializer,
    }

    @action(methods=["POST"], detail=False)
    def batch_import(self, request, *args, **kwargs):
        data = super().batch_import(request, *args, preview=True, **kwargs)
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, many=True if isinstance(request.data, list) else False
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
