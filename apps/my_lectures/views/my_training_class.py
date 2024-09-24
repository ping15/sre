from rest_framework.decorators import action

from apps.my_lectures.serializers.my_training_class import (
    MyTrainingClassListSerializer,
    MyTrainingClassRetrieveSerializer,
)
from apps.platform_management.filters.all_classes import AllClassesFilterClass
from apps.teaching_space.models import TrainingClass
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import InstructorPermission
from common.utils.drf.response import Response


class MyTrainingClassViewSet(ModelViewSet):
    permission_classes = [InstructorPermission]
    queryset = TrainingClass.objects.all()
    filter_class = AllClassesFilterClass
    http_method_names = ["get"]
    ACTION_MAP = {
        "list": MyTrainingClassListSerializer,
        "retrieve": MyTrainingClassRetrieveSerializer,
    }

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "target_client_company_name", "name": "客户公司", "children": []},
                {"id": "name", "name": "培训班名称", "children": []},
                {"id": "location", "name": "上课地点", "children": []},
            ]
        )
