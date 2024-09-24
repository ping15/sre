from django.db.models import QuerySet

from apps.my_lectures.handles.event import EventHandler
from apps.my_lectures.serializers.schedule import (
    EventCreateSerializer,
    EventListSerializer,
    EventUpdateSerializer,
)
from apps.platform_management.models import Event, Instructor
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import InstructorPermission
from common.utils.drf.response import Response


class ScheduleModelViewSet(ModelViewSet):
    permission_classes = [InstructorPermission]
    queryset = Event.objects.all()
    ACTION_MAP = {
        "list": EventListSerializer,
        "create": EventCreateSerializer,
        "update": EventUpdateSerializer,
    }

    def list(self, request, *args, **kwargs):
        user: Instructor = self.request.user
        validated_data = self.validated_data

        events: QuerySet["Event"] = self.get_queryset().filter(instructor=user)
        return Response(EventHandler.build_calendars(events, validated_data["start_date"], validated_data["end_date"]))

    def create(self, request, *args, **kwargs):
        """日程规则创建"""
        EventHandler.create_event(
            **self.validated_data, instructor=self.request.user
        )
        return Response()

    def update(self, request, *args, **kwargs):
        if self.get_object().instructor != self.request.user:
            return Response(result=False, err_msg="该规则不是由该讲师创建的，不可编辑")

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().instructor != self.request.user:
            return Response(result=False, err_msg="该规则不是由该讲师创建的，不可删除")

        return super().destroy(request, *args, **kwargs)
