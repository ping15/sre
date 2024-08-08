from typing import Dict

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
    fuzzy_filter_fields = ["af"]
    ACTION_MAP = {
        "list": AllScheduleSerializer,
    }

    def list(self, request, *args, **kwargs):
        validated_data = self.validated_data

        date__daily_calendar_map: Dict[str, dict] = generate_blank_calendar(
            validated_data["year"], validated_data["month"]
        )

        inject_training_class_to_calendar(date__daily_calendar_map, self.queryset)

        return Response(date__daily_calendar_map)
