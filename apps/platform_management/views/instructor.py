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
    InstructorUpdateSerializer,
    InstructorPartialUpdateSerializer,
)
from apps.teaching_space.models import TrainingClass
from common.utils.calander import (
    generate_blank_calendar,
    inject_training_class_to_calendar,
)
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
    string_fuzzy_filter_fields = ["username", "introduction"]
    ACTION_MAP = {
        "list": InstructorListSerializer,
        "create": InstructorCreateSerializer,
        "retrieve": InstructorRetrieveSerializer,
        "calendar": InstructorCalendarSerializer,
        "review": InstructorReviewSerializer,
        "update": InstructorUpdateSerializer,
        "partial_update": InstructorPartialUpdateSerializer,
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
            string_fuzzy_filter_fields=["target_client_company_name"],
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
        return Response(
            [
                {"id": "name", "name": "培训班名称", "children": []},
                {"id": "target_client_company_name", "name": "客户公司", "children": []},
                {"id": "start_date", "name": "时间", "children": []},
            ]
        )

    @action(methods=["GET"], detail=True)
    def calendar(self, request, *args, **kwargs):
        """日程"""
        validated_data = self.validated_data

        date__daily_calendar_map: Dict[str, dict] = generate_blank_calendar(
            validated_data["year"], validated_data["month"]
        )

        inject_training_class_to_calendar(
            date__daily_calendar_map, self.get_object().training_classes.all()
        )

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

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "username", "name": "讲师名称", "children": []},
                {"id": "introduction", "name": "简介", "children": []},
            ]
        )
