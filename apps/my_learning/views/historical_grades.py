from rest_framework.decorators import action

from apps.platform_management.models import ClientStudent
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    ManageCompanyAdministratorPermission,
    StudentPermission,
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response
from exam_system.models import ExamStudent


class HistoricalGradesApiView(ModelViewSet):
    permission_classes = [StudentPermission]
    queryset = ExamStudent.objects.all()
    http_method_names = ["get"]

    PERMISSION_MAP = {
        "filter_condition": [StudentPermission | SuperAdministratorPermission | ManageCompanyAdministratorPermission],
    }

    # region 列表
    def list(self, request, *args, **kwargs):
        user: ClientStudent = self.request.user

        return self.build_student_grades_response(student=user, query_params=request.query_params)

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response([
            {"id": "training_class_name", "name": "培训班名称", "children": []},
            {"id": "exam_title", "name": "考试名称", "children": []},
        ])
    # endregion
