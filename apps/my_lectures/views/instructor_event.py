import datetime

from django.db import transaction
from django.db.models import QuerySet
from rest_framework.decorators import action

from apps.my_lectures.filters.instructor_event import InstructorEventFilterClass
from apps.my_lectures.handles.event import EventHandler
from apps.my_lectures.models import InstructorEvent
from apps.my_lectures.serializers.instructor_event import (
    InstructorEventListSerializer,
    InstructorEventRetrieveSerializer,
    InstructorEventUpdateReviewSerializer,
    InstructorEventUpdateStatusSerializer,
)
from apps.platform_management.models import Event
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import InstructorPermission
from common.utils.drf.response import Response


class InstructorEventModelViewSet(ModelViewSet):
    permission_classes = [InstructorPermission]
    queryset = InstructorEvent.objects.all()
    filter_class = InstructorEventFilterClass
    http_method_names = ["get", "post"]
    ACTION_MAP = {
        "list": InstructorEventListSerializer,
        "retrieve": InstructorEventRetrieveSerializer,
        "update_status": InstructorEventUpdateStatusSerializer,
        "update_review": InstructorEventUpdateReviewSerializer,
    }

    def get_queryset(self):
        queryset: QuerySet["InstructorEvent"] = super().get_queryset()
        return queryset.filter(instructor=self.request.user)

    def list(self, request, *args, **kwargs):
        # 已经过了[截至时间且未处理的单据更新为已超时
        self.get_queryset().filter(
            start_date__lte=datetime.datetime.now().date(),
            status=InstructorEvent.Status.PENDING,
            event_type=InstructorEvent.EventType.INVITE_TO_CLASS
        ).update(
            status=InstructorEvent.Status.TIMEOUT
        )

        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return Response(result=False)

    @action(detail=True, methods=["POST"])
    def update_status(self, request, *args, **kwargs):
        validated_data = self.validated_data

        instructor_event: InstructorEvent = self.get_object()

        # 非[邀请上课]类型事件不可更新状态
        if instructor_event.event_type != InstructorEvent.EventType.INVITE_TO_CLASS:
            return Response(result=False, err_msg="该单据类型不属于[邀请上课]")

        if instructor_event.status == InstructorEvent.Status.TIMEOUT.value:
            return Response(result=False, err_msg="该单据已过期")

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

    @action(detail=True, methods=["POST"])
    def update_review(self, request, *args, **kwargs):
        validated_data = self.validated_data

        instructor_event: InstructorEvent = self.get_object()

        # 非[课后复盘]类型事件不可填写课后复盘
        if instructor_event.event_type != InstructorEvent.EventType.POST_CLASS_REVIEW:
            return Response(result=False, err_msg="该单据类型不属于[课后复盘]，不可填写课后复盘")

        if instructor_event.status == InstructorEvent.Status.TIMEOUT.value:
            return Response(result=False, err_msg="该单据已过期")

        if instructor_event.status != InstructorEvent.Status.PENDING.value:
            return Response(result=False, err_msg="该单据已处理")

        with transaction.atomic():
            # 填写课后复盘
            instructor_event.review = validated_data["review"]

            # 更新单据状态
            instructor_event.status = InstructorEvent.Status.FINISHED
            instructor_event.save()

        return Response()

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response([
            {"id": "event_name", "name": "事项名", "children": []},
            {"id": "initiator", "name": "事项发起人", "children": []},
            {"id": "created_datetime", "name": "发起时间", "children": []},
            {"id": "status", "name": "事项状态", "children": [
                {"id": status.value, "name": status.label}
                for status in InstructorEvent.Status.get_completed_statuses()
            ]},
        ])
