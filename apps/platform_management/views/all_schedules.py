from collections import defaultdict

from django.db.models import QuerySet
from rest_framework.decorators import action

from apps.my_lectures.handles.event import EventHandler
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
            EventHandler.build_calendars(
                self.filter_queryset(
                    self.get_queryset().filter(
                        event_type=Event.EventType.CLASS_SCHEDULE.value
                    )
                ),
                validated_data["start_date"],
                validated_data["end_date"],
            )
        )

    @staticmethod
    def aggregate_items(queryset, field_name):
        aggregation_dict = defaultdict(list)
        for item in queryset:
            field_value = getattr(item, field_name)
            aggregation_dict[field_value].append(str(item.id))
        return [
            {"id": ",".join(ids), "name": name}
            for name, ids in aggregation_dict.items()
        ]

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {
                    "id": "manage_company",
                    "name": "管理公司",
                    "children": self.aggregate_items(
                        ManageCompany.objects.all(), "name"
                    ),
                },
                {
                    "id": "client_company",
                    "name": "客户公司",
                    "children": self.aggregate_items(
                        ClientCompany.objects.all(), "name"
                    ),
                },
                {
                    "id": "instructor",
                    "name": "讲师",
                    "children": self.aggregate_items(
                        Instructor.objects.all(), "username"
                    ),
                },
                {
                    "id": "training_classes",
                    "name": "培训班",
                    "children": self.aggregate_items(
                        TrainingClass.objects.all(), "name"
                    ),
                },
            ]
        )
