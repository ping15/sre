import datetime

from django.db import transaction
from django.db.models import QuerySet

from apps.my_lectures.filters.instructor_event import InstructorEventFilterClass
from apps.my_lectures.handles.event import EventHandler
from apps.my_lectures.models import InstructorEvent
from apps.my_lectures.serializers.instructor_event import (
    InstructorEventListSerializer,
    InstructorEventUpdateSerializer,
)
from apps.platform_management.models import Event
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import InstructorPermission
from common.utils.drf.response import Response


class InstructorEventModelViewSet(ModelViewSet):
    permission_classes = [InstructorPermission]
    queryset = InstructorEvent.objects.all()
    filter_class = InstructorEventFilterClass
    ACTION_MAP = {
        "list": InstructorEventListSerializer,
        "update": InstructorEventUpdateSerializer,
        "partial_update": InstructorEventUpdateSerializer,
    }

    def get_queryset(self):
        queryset: QuerySet["InstructorEvent"] = super().get_queryset()
        return queryset.filter(instructor=self.request.user)

    def list(self, request, *args, **kwargs):
        # 已经过了截至时间的单据更新为已超时
        self.get_queryset().filter(start_date__lte=datetime.datetime.now().date()).update(
            status=InstructorEvent.Status.TIMEOUT)

        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        validated_data = self.validated_data

        instructor_event: InstructorEvent = self.get_object()
        if instructor_event.status != InstructorEvent.Status.PENDING.value:
            return Response(result=False, err_msg="该单据已处理")

        with transaction.atomic():
            # 单据状态流转
            instructor_event.status = validated_data["status"]
            instructor_event.save()

            # 1. 同意则新增日程
            # 2. 因讲师无法同时在一天内给多个客户公司上课，其他单据与当前单据有时间冲突的自动流转为已拒绝
            if validated_data["status"] == InstructorEvent.Status.AGREED.value:
                EventHandler.create_event(
                    training_class=instructor_event.training_class, event_type=Event.EventType.CLASS_SCHEDULE.value)

        return Response()
