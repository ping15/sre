import datetime
import os
from datetime import timedelta, date
from typing import List, Dict

from django.db.models import QuerySet
from django.http import Http404, FileResponse
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet as DRFModelViewSet

from apps.platform_management.models import Event
from apps.teaching_space.models import TrainingClass
from common.utils.calendar import generate_blank_calendar, between, format_date
from common.utils.drf.filters import BaseFilterSet
from common.utils.drf.response import Response
from common.utils.excel_parser.parser import excel_to_list


class FileSerializer(serializers.Serializer):
    file_path = serializers.CharField()


class SimpleQuerySerializer(serializers.Serializer):
    query = serializers.CharField()


class ModelViewSet(DRFModelViewSet):
    # 是否支持批量导入
    enable_batch_import = False
    batch_import_serializer = None
    batch_import_template_path = ""
    batch_import_mapping = {}

    # 默认序列化器
    default_serializer_class = None

    # 备份filter_backend
    # origin_filter_backend = api_settings.DEFAULT_FILTER_BACKENDS

    # 视图 -> 序列化器
    ACTION_MAP = {}

    # 筛选, fuzzy: 模糊匹配, time/datetime: 时间匹配, property: 属性匹配,
    filter_class = BaseFilterSet
    # copy_filter_class = filter_class
    # # string模糊匹配
    # string_fuzzy_filter_fields = []
    # # integer匹配
    # integer_filter_fields = []
    # # time匹配
    # time_filter_fields = []
    # # datetime匹配
    # datetime_filter_fields = []
    # # property模糊匹配
    # property_fuzzy_filter_fields = []

    # 页面关键词 -> 字段
    filter_condition_mapping = {}
    # filter_condition_enum_list = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.enable_batch_import and hasattr(cls, "batch_import"):
            cls.batch_import = None
            cls.batch_import_template = None
        else:
            cls.ACTION_MAP["batch_import"] = FileSerializer
            if not cls.batch_import_serializer:
                cls.batch_import_serializer = cls.ACTION_MAP.get("create")

        cls.ACTION_MAP["simple_query"] = SimpleQuerySerializer

    def get_serializer_class(self):
        return self.ACTION_MAP.get(self.action, self.default_serializer_class)  # noqa

    @property
    def validated_data(self):
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, many=True if isinstance(request.data, list) else False
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return Response(super().update(request, *args, **kwargs).data)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response(result=False, err_msg=e.args[0])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        response_data = []

        for display_name, field_name in self.filter_condition_mapping.items():
            item = {"id": field_name, "name": display_name, "children": []}

            response_data.append(item)

        return Response(response_data)

    @action(methods=["POST"], detail=False)
    def batch_import(self, request, *args, **kwargs):
        """批量导入"""
        validated_data = self.validated_data
        datas: List[Dict[str, str]] = excel_to_list(
            validated_data["file_path"], self.batch_import_mapping
        )
        create_serializer = self.batch_import_serializer(data=datas, many=True)

        if not create_serializer.is_valid():
            return Response(
                data=[], result=False, err_msg=str(create_serializer.errors)
            )

        return Response(create_serializer.validated_data)

    @action(methods=["GET"], detail=False)
    def batch_import_template(self, request, *args, **kwargs):
        if not os.path.exists(self.batch_import_template_path):
            raise Http404("Template file does not exist")

        response = FileResponse(
            open(self.batch_import_template_path, "rb"),
            as_attachment=True,
            filename=os.path.basename(self.batch_import_template_path),
        )
        return response

    @action(methods=["GET"], detail=False)
    def simple_query(self, request, *args, **kwargs):
        validated_data = self.validated_data
        return Response(list(self.queryset.values(*validated_data["query"].split(","))))

    @classmethod
    def build_calendars(
        cls, events: QuerySet["Event"], start_date: date, end_date: date
    ) -> List[dict]:
        blank_calendar: Dict[str, dict] = generate_blank_calendar(start_date, end_date)

        # events = events.filter(end_date__gte=start_date, start_date__lt=end_date).order_by("type")

        for event in events:
            event_start_date, event_end_date = event.start_date, event.end_date
            marking_start_date = max(start_date, event_start_date)

            # 如果未设置结束时间，以传入的结束时间作为最终的结束时间
            if not event_end_date:
                marking_end_date = end_date
            else:
                marking_end_date = min(end_date, event_end_date)

            # 培训班排课
            if event.type == Event.Type.CLASS_SCHEDULE.value:
                blank_calendar[format_date(marking_start_date)]["count"] += 1
                blank_calendar[format_date(marking_start_date)]["data"].append(
                    cls.build_event_data(event)
                )

            # 取消单日不可用时间
            elif event.type == Event.Type.CANCEL_UNAVAILABILITY.value:
                assert event_start_date == event_end_date
                cls.marking_canceled(
                    blank_calendar, marking_start_date, marking_end_date
                )

            # 登记一次性不可用时间规则和周期性不可用时间规则
            elif event.type in [
                Event.Type.ONE_TIME_UNAVAILABILITY.value,
                Event.Type.RECURRING_UNAVAILABILITY.value,
            ]:
                # blank_calendar[format_date(marking_start_date)]["rules"].append(cls.build_event_data(event))
                cls.marking_unavailable(
                    blank_calendar, event, marking_start_date, marking_end_date
                )

        blank_calendar = {
            current_date: calendar_info
            for current_date, calendar_info in blank_calendar.items()
            if calendar_info["data"]
            or calendar_info["rules"]
            or not calendar_info["is_available"]
        }

        # 将字典转换为列表并按 start_date 排序
        return sorted(blank_calendar.values(), key=lambda x: x["date"])

    @classmethod
    def build_event_data(cls, event: Event):
        if event.type == Event.Type.CLASS_SCHEDULE.value:
            training_class: TrainingClass = event.training_class
            return {
                "id": training_class.id,
                "start_date": training_class.start_date,
                "end_date": training_class.start_date + datetime.timedelta(days=1),
                "target_client_company_name": training_class.target_client_company_name,
                "instructor_name": training_class.instructor_name,
                "name": training_class.name,
            }

        return {
            "id": event.id,
            "freq_type": event.freq_type,
            "freq_interval": event.freq_interval,
            "start_date": event.start_date,
            "end_date": event.end_date,
            "training_class": event.training_class,
        }

    @classmethod
    def marking_unavailable(
        cls,
        blank_calendar: Dict[str, dict],
        event: Event,
        start_date: date,
        end_date: date,
    ):
        event_type = event.type
        for current_date in between(start_date, end_date):
            if blank_calendar[format_date(current_date)]["is_canceled"]:
                continue

            if event_type == Event.Type.ONE_TIME_UNAVAILABILITY.value:
                cls._mark_unavailable(blank_calendar, event, current_date)

            elif event_type == Event.Type.RECURRING_UNAVAILABILITY.value:
                freq_type, freq_internal = event.freq_type, event.freq_interval
                if (
                    freq_type == Event.FreqType.WEEKLY
                    and current_date.isoweekday() in freq_internal
                ):
                    cls._mark_unavailable(blank_calendar, event, current_date)

                elif (
                    freq_type == Event.FreqType.MONTHLY
                    and current_date.day in freq_internal
                ):
                    cls._mark_unavailable(blank_calendar, event, current_date)

    @classmethod
    def _mark_unavailable(
        cls, blank_calendar: Dict[str, dict], event: Event, current_date: date
    ):
        blank_calendar[format_date(current_date)]["is_available"] = False
        blank_calendar[format_date(current_date)]["rules"].append(
            cls.build_event_data(event)
        )

    @classmethod
    def marking_canceled(
        cls, blank_calendar: Dict[str, dict], start_date: date, end_date: date
    ):
        for current_date in between(start_date, end_date):
            blank_calendar[format_date(current_date)]["is_canceled"] = True
            blank_calendar[format_date(current_date)]["is_available"] = True
