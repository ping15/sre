from django.db import transaction
from rest_framework.permissions import AllowAny

from apps.my_lectures.handles.event import EventHandler
from apps.my_lectures.models import InstructorEvent
from apps.my_lectures.serializers.instructor_event import (
    InstructorEventListSerializer, InstructorEventUpdateSerializer)
from apps.platform_management.models import Event
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.response import Response


class InstructorEventModelViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = InstructorEvent.objects.all()
    ACTION_MAP = {
        "list": InstructorEventListSerializer,
        "update": InstructorEventUpdateSerializer,
    }

    def update(self, request, *args, **kwargs):
        validated_data = self.validated_data

        instructor_event: InstructorEvent = self.get_object()
        if instructor_event.status != InstructorEvent.Status.PENDING.value:
            return Response(result=False, err_msg="该单据已处理")

        with transaction.atomic():
            # 单据状态扭转
            instructor_event.status = validated_data["status"]
            instructor_event.save()

            # 同意则新增日程
            if validated_data["status"] == InstructorEvent.Status.AGREED.value:
                EventHandler.create_event(
                    training_class=instructor_event.training_class, event_type=Event.EventType.CLASS_SCHEDULE.value)

        return Response()
