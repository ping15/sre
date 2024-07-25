import datetime
from datetime import timedelta
from typing import List, Dict

from rest_framework.decorators import action
from rest_framework.response import Response

from apps.platform_management.models import Instructor
from apps.platform_management.serialiers.instructor import (
    InstructorListSerializer,
    InstructorCreateSerializer,
    InstructorCalendarSerializer,
    InstructorRetrieveSerializer,
    InstructorReviewSerializer,
)
from common.utils.calander import generate_calendar
from common.utils.excel_parser.mapping import INSTRUCTOR_EXCEL_MAPPING
from common.utils.modelviewset import ModelViewSet
from common.utils.permissions import InstructorPermission


class InstructorModelViewSet(ModelViewSet):
    permission_classes = [InstructorPermission]
    default_serializer_class = InstructorCreateSerializer
    queryset = Instructor.objects.all()
    enable_batch_import = True
    batch_import_mapping = INSTRUCTOR_EXCEL_MAPPING
    ACTION_MAP = {
        "list": InstructorListSerializer,
        "create": InstructorCreateSerializer,
        "retrieve": InstructorRetrieveSerializer,
        "calendar": InstructorCalendarSerializer,
        "review": InstructorReviewSerializer,
    }

    @action(methods=["GET"], detail=True)
    def taught_courses(self, request, *args, **kwargs):
        """已授课程"""
        taught_courses: List[Dict[str:str]] = []
        training_classes = self.get_object().training_classes.filter(
            start_date__lte=datetime.datetime.now()
        )

        for instance in training_classes:
            taught_courses.append(
                {
                    "name": instance.name,
                    "hours": instance.hours_per_lesson,
                    "start_date": instance.start_date,
                    "target_client_company": instance.target_client_company,
                }
            )

        return self.get_paginated_response(self.paginate_queryset(taught_courses))

    @action(methods=["GET"], detail=True)
    def calendar(self, request, *args, **kwargs):
        """日程"""
        validated_data = self.validated_data

        # 培训班信息
        training_classes_info: List[dict] = [
            {
                "start_date": instance.start_date,
                "target_client_company": instance.target_client_company,
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
        mock_data = [
            {
                "course_name": "SRE 专家培训课(中级)",
                "target_client_company": "客户公司名称A",
                "finish_date": "2024-10-24",
                "review": "复盘内容......",
            },
            {
                "course_name": "SRE 专家培训课(高级)",
                "target_client_company": "客户公司名称B",
                "finish_date": "2024-10-25",
                "review": "复盘内容......",
            },
        ]
        return Response(mock_data)
