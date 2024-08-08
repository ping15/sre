from typing import Dict

from rest_framework.decorators import action

from apps.platform_management.filters.all_schedules import AllScheduleFilterClass
from apps.platform_management.models import ManageCompany, ClientCompany, Instructor
from apps.teaching_space.models import TrainingClass
from apps.platform_management.serialiers.all_schedules import AllScheduleSerializer
from common.utils.calander import (
    generate_blank_calendar,
    inject_training_class_to_calendar,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission
from common.utils.drf.response import Response


class AllScheduleModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    queryset = TrainingClass.objects.all()
    filter_class = AllScheduleFilterClass
    ACTION_MAP = {
        "list": AllScheduleSerializer,
    }

    def list(self, request, *args, **kwargs):
        validated_data = self.validated_data

        date__daily_calendar_map: Dict[str, dict] = generate_blank_calendar(
            validated_data["year"], validated_data["month"]
        )

        inject_training_class_to_calendar(
            date__daily_calendar_map, self.filter_queryset(self.queryset)
        )

        return Response(date__daily_calendar_map)

    @staticmethod
    def get_unique_children(queryset, name_field):
        seen_names = set()
        unique_children = []
        for item in queryset:
            name = getattr(item, name_field)
            if name not in seen_names:
                seen_names.add(name)
                unique_children.append({"id": item.id, "name": name})
        return unique_children

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {
                    "id": "manage_company",
                    "name": "管理公司",
                    "children": self.get_unique_children(
                        ManageCompany.objects.all(), "name"
                    ),
                },
                {
                    "id": "client_company",
                    "name": "客户公司",
                    "children": self.get_unique_children(
                        ClientCompany.objects.all(), "name"
                    ),
                },
                {
                    "id": "instructor",
                    "name": "讲师",
                    "children": self.get_unique_children(
                        Instructor.objects.all(), "username"
                    ),
                },
                {
                    "id": "training_classes",
                    "name": "培训班",
                    "children": self.get_unique_children(
                        TrainingClass.objects.all(), "name"
                    ),
                },
            ]
        )
