import datetime
from datetime import timedelta
from typing import Dict, List, Set

from django.db.models import QuerySet
from rest_framework.decorators import action

from apps.my_lectures.handles.event import EventHandler
from apps.platform_management.filters.instructor import (
    InstructorFilterClass,
    InstructorTaughtCoursesFilterClass,
)
from apps.platform_management.models import Event, Instructor
from apps.platform_management.serialiers.instructor import (
    InstructorCalendarSerializer,
    InstructorCreateSerializer,
    InstructorFilterConditionSerializer,
    InstructorListSerializer,
    InstructorPartialUpdateSerializer,
    InstructorRetrieveSerializer,
    InstructorReviewSerializer,
    InstructorUpdateSerializer,
)
from apps.teaching_space.models import TrainingClass
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    ManageCompanyAdministratorPermission,
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response
from common.utils.excel_parser.mapping import INSTRUCTOR_EXCEL_MAPPING
from common.utils.global_constants import AppModule


class InstructorModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    serializer_class = InstructorCreateSerializer
    queryset = Instructor.objects.all()
    enable_batch_import = True
    batch_import_template_path = "common/utils/excel_parser/templates/讲师批量导入模板.xlsx"
    batch_import_mapping = INSTRUCTOR_EXCEL_MAPPING
    filter_class = InstructorFilterClass
    ACTION_MAP = {
        "list": InstructorListSerializer,
        "create": InstructorCreateSerializer,
        "retrieve": InstructorRetrieveSerializer,
        "calendar": InstructorCalendarSerializer,
        "review": InstructorReviewSerializer,
        "update": InstructorUpdateSerializer,
        "partial_update": InstructorPartialUpdateSerializer,
        "filter_condition": InstructorFilterConditionSerializer,
    }
    PERMISSION_MAP = {
        "list": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
        "filter_condition": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
    }

    @action(methods=["GET"], detail=True)
    def taught_courses(self, request, *args, **kwargs):
        """已授课程"""
        taught_courses: List[Dict[str:str]] = []

        training_classes: QuerySet["TrainingClass"] = self.get_object().training_classes.filter(
            start_date__lte=datetime.datetime.now()
        )

        self.filter_class = InstructorTaughtCoursesFilterClass
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

        return Response(
            EventHandler.build_calendars(
                Event.objects.all(),
                start_date=validated_data["start_date"],
                end_date=validated_data["end_date"],
            )
        )

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
        validated_data = self.validated_data

        cities: Set[str] = {instructor.city for instructor in Instructor.objects.all()}

        if validated_data["module"] == AppModule.PLATFORM_MANAGEMENT.value:
            return Response([
                {"id": "username", "name": "讲师名称", "children": []},
                {"id": "introduction", "name": "简介", "children": []},
            ])

        elif validated_data["module"] == AppModule.TEACHING_SPACE.value:
            return Response([
                {"id": "username", "name": "讲师名称", "children": []},
                {"id": "satisfaction_score", "name": "讲师评分", "children": []},
                {"id": "city", "name": "城市", "children": [
                    {"id": city, "name": city}
                    for city in cities
                ]},
                {"id": "availability_date", "name": "讲师可预约时间", "children": []},
            ])

        return Response([])
