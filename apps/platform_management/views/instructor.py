import datetime
from datetime import timedelta
from typing import List, Dict

from django.db.models import QuerySet
from rest_framework.decorators import action

from apps.platform_management.models import Instructor
from apps.platform_management.serialiers.instructor import (
    InstructorListSerializer,
    InstructorCreateSerializer,
    InstructorCalendarSerializer,
    InstructorRetrieveSerializer,
    InstructorReviewSerializer,
)
from apps.teaching_space.models import TrainingClass
from common.utils.calander import generate_calendar
from common.utils.drf.response import Response
from common.utils.excel_parser.mapping import INSTRUCTOR_EXCEL_MAPPING
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission


class InstructorModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    default_serializer_class = InstructorCreateSerializer
    queryset = Instructor.objects.all()
    enable_batch_import = True
    batch_import_mapping = INSTRUCTOR_EXCEL_MAPPING
    fuzzy_filter_fields = ["name", "introduction"]
    filter_condition_mapping = {
        "讲师名称": "name",
        "简介": "introduction",
    }
    ACTION_MAP = {
        "list": InstructorListSerializer,
        "create": InstructorCreateSerializer,
        "retrieve": InstructorRetrieveSerializer,
        "calendar": InstructorCalendarSerializer,
        "review": InstructorReviewSerializer,
    }

    def list(self, request, *args, **kwargs):
        print(f"user={request.user}")
        return super().list(request, *args, **kwargs)

    @action(methods=["GET"], detail=True)
    def taught_courses(self, request, *args, **kwargs):
        """已授课程"""
        taught_courses: List[Dict[str:str]] = []

        # 禁用讲师的筛选
        self.disable_filter_backend()
        training_classes: QuerySet[
            "TrainingClass"
        ] = self.get_object().training_classes.filter(
            start_date__lte=datetime.datetime.now()
        )

        # 重构筛选为培训班并启用筛选
        self.filter_class.setup_filters(
            TrainingClass,
            property_fuzzy_filter_fields=["name"],
            fuzzy_filter_fields=["target_client_company_name"],
            time_filter_fields=["start_date"],
        )
        self.enable_filter_backend()
        training_classes = self.filter_queryset(training_classes)

        for instance in training_classes:
            taught_courses.append(
                {
                    "name": instance.name,
                    "hours": instance.hours_per_lesson,
                    "start_date": instance.start_date,
                    "target_client_company_name": instance.target_client_company_name,
                }
            )

        return self.get_paginated_response(self.paginate_queryset(taught_courses))

    @action(methods=["GET"], detail=True, url_path="taught_courses/filter_condition")
    def taught_courses_filter_condition(self, request, *args, **kwargs):
        self.filter_condition_mapping = {
            "培训班名称": "name",
            "客户公司": "target_client_company_name",
            "时间": "start_date",
        }
        return self.filter_condition(request, *args, **kwargs)

    @action(methods=["GET"], detail=True)
    def calendar(self, request, *args, **kwargs):
        """日程"""
        validated_data = self.validated_data

        # 培训班信息
        training_classes_info: List[dict] = [
            {
                "id": instance.id,
                "start_date": instance.start_date,
                "target_client_company_name": instance.target_client_company_name,
                "name": instance.name,
            }
            for instance in self.get_object().training_classes.all()
        ]
        date__daily_calendar_map: Dict[str, dict] = generate_calendar(
            validated_data["year"], validated_data["month"]
        )
        for programme in training_classes_info:
            start_date: datetime.date = programme.pop("start_date")
            formatted_start_date: str = start_date.strftime("%Y-%m-%d")
            formatted_next_date: str = (start_date + timedelta(days=1)).strftime(
                "%Y-%m-%d"
            )

            # 更新当前日期的日历映射
            if formatted_start_date in date__daily_calendar_map:
                date__daily_calendar_map[formatted_start_date]["data"].append(programme)
                date__daily_calendar_map[formatted_start_date]["count"] += 1

            # 更新下一天的日历映射
            if formatted_next_date in date__daily_calendar_map:
                date__daily_calendar_map[formatted_next_date]["data"].append(programme)
                date__daily_calendar_map[formatted_next_date]["count"] += 1

        return Response(date__daily_calendar_map.values())

    @action(methods=["GET"], detail=True)
    def review(self, request, *args, **kwargs):
        """课后复盘"""
        taught_courses: List[Dict[str:str]] = []
        training_classes: QuerySet[
            TrainingClass
        ] = self.get_object().training_classes.filter(
            start_date__gte=datetime.datetime.now() + datetime.timedelta(days=1)
        )

        for instance in training_classes:
            taught_courses.append(
                {
                    "course_name": instance.name,
                    "target_client_company_name": instance.target_client_company_name,
                    "finish_date": instance.start_date + timedelta(days=1),
                    "review": instance.review,
                }
            )

        return self.get_paginated_response(self.paginate_queryset(taught_courses))
