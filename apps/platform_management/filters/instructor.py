import datetime
from typing import List

import django_filters
from django.db.models import QuerySet

from apps.my_lectures.handles.event import EventHandler
from apps.platform_management.models import CourseTemplate, Instructor
from common.utils import global_constants
from common.utils.drf.filters import BaseFilterSet, DynamicRangeFilter, PropertyFilter


class InstructorFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username", label="讲师名称")
    introduction = django_filters.CharFilter("introduction", label="简介")
    satisfaction_score = DynamicRangeFilter(field_name="satisfaction_score", label="讲师评分")
    city = django_filters.CharFilter("city", lookup_expr="exact", label="城市")
    availability_date = django_filters.DateFilter(method="filter_availability_date", label="可预约时间")
    course_id = django_filters.NumberFilter(method="filter_course_id", label="培训班授课课程id")
    is_partnered = django_filters.BooleanFilter("is_partnered", label="是否合作", lookup_expr="exact")

    @staticmethod
    def filter_availability_date(queryset: QuerySet["Instructor"], name: str, today: datetime.date):
        instructor_ids: List = []
        for instructor in queryset:
            if EventHandler.is_instructor_idle(
                instructor=instructor,
                start_date=today,
                end_date=today + datetime.timedelta(days=global_constants.CLASS_DAYS - 1)
            ):
                instructor_ids.append(instructor.id)

        return queryset.filter(id__in=instructor_ids)

    @staticmethod
    def filter_course_id(queryset: QuerySet["Instructor"], name: str, course_id: int):
        try:
            course_name = CourseTemplate.objects.get(id=course_id).name
            return queryset.filter(teachable_courses__contains=[course_name])

        except (CourseTemplate.DoesNotExist, CourseTemplate.MultipleObjectsReturned):
            return queryset


class InstructorTaughtCoursesFilterClass(BaseFilterSet):
    name = PropertyFilter("name", label="培训班名称")
    target_client_company_name = django_filters.CharFilter(
        "target_client_company_name", lookup_expr="icontains", label="客户公司")
    start_date = django_filters.DateFromToRangeFilter("start_date", "开课时间")
