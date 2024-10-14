from rest_framework.decorators import action

from apps.platform_management.filters.all_classes import AllClassesFilterClass
from apps.platform_management.serialiers.all_classes import AllClassesListSerializer
from apps.teaching_space.models import TrainingClass
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission
from common.utils.drf.response import Response


class AllClassesModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    queryset = TrainingClass.objects.all()
    filter_class = AllClassesFilterClass
    http_method_names = ["get"]
    ACTION_MAP = {
        "list": AllClassesListSerializer,
    }

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "target_client_company_name", "name": "客户公司", "children": []},
                {
                    "id": "affiliated_manage_company_name",
                    "name": "管理公司",
                    "children": [],
                },
                {"id": "name", "name": "培训班名称", "children": []},
                {"id": "instructor_name", "name": "讲师", "children": []},
                {"id": "location", "name": "上课地点", "children": []},
                {"id": "start_date", "name": "时间", "children": []},
            ]
        )
