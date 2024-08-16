from rest_framework.decorators import action

from apps.platform_management.filters.all_schedules import AllScheduleFilterClass
from apps.platform_management.models import (
    ManageCompany,
    ClientCompany,
    Instructor,
    Event,
)
from apps.teaching_space.models import TrainingClass
from apps.platform_management.serialiers.all_schedules import (
    AllScheduleListSerializer,
    AllScheduleCreateSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission
from common.utils.drf.response import Response


class AllScheduleModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    queryset = Event.objects.all()
    filter_class = AllScheduleFilterClass
    ACTION_MAP = {
        "list": AllScheduleListSerializer,
        "create": AllScheduleCreateSerializer,
    }

    def list(self, request, *args, **kwargs):
        validated_data = self.validated_data
        return Response(
            self.build_calendars(
                self.get_queryset(),
                validated_data["start_date"],
                validated_data["end_date"],
            )
        )

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
