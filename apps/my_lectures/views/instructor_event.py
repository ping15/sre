import datetime

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
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
from apps.teaching_space.models import TrainingClass
from common.utils import global_constants
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
        # 查询已经过了[截至时间]且[未处理]的单据
        timeout_instructor_events: QuerySet[InstructorEvent] = self.get_queryset().filter(
            start_date__lte=timezone.now().date(),
            status=InstructorEvent.Status.PENDING,
            event_type=InstructorEvent.EventType.INVITE_TO_CLASS
        )

        # 将单据状态为已超时
        timeout_instructor_events.update(status=InstructorEvent.Status.TIMEOUT)

        # 培训班发布状态修改为[未发布]
        TrainingClass.objects. \
            filter(instructor_event__in=timeout_instructor_events). \
            update(publish_type=TrainingClass.PublishType.NONE)

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
                # 修改开课时间，优先使用可预约时间，如果没有默认使用培训班开课时间
                training_class: TrainingClass = instructor_event.training_class
                # training_class.start_date = instructor_event.start_date
                # training_class.save()

                # 新增日程
                EventHandler.create_event(
                    training_class=training_class, event_type=Event.EventType.CLASS_SCHEDULE.value)

                # 将单据状态为[待处理]，且时间与该单据有冲突的自动修改为[已拒绝]
                self.get_queryset(). \
                    filter(
                        status=InstructorEvent.Status.PENDING,
                        start_date__range=(
                            instructor_event.start_date,
                            instructor_event.start_date + datetime.timedelta(days=global_constants.CLASS_DAYS - 1))). \
                    update(status=InstructorEvent.Status.REJECTED)

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

            # 更新培训班的课后复盘
            training_class: TrainingClass = instructor_event.training_class
            training_class.review = validated_data["review"]
            training_class.save()

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
