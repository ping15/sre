import datetime
from decimal import Decimal
from typing import List

import django_filters
from django.db.models import Q, QuerySet

from apps.my_lectures.handles.event import EventHandler
from apps.platform_management.models import CourseTemplate, Event, Instructor
from common.utils import global_constants
from common.utils.drf.filters import BaseFilterSet, DynamicRangeFilter, PropertyFilter
from common.utils.tools import query_debugger


class InstructorFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username", label="讲师名称")
    introduction = django_filters.CharFilter("introduction", label="简介")
    satisfaction_score = DynamicRangeFilter(field_name="satisfaction_score", label="讲师评分")
    city = django_filters.CharFilter("city", lookup_expr="exact", label="城市")
    availability_date = django_filters.DateFilter(method="filter_availability_date", label="可预约时间")
    course_id = django_filters.NumberFilter(method="filter_course_id", label="培训班授课课程id")
    is_partnered = django_filters.BooleanFilter("is_partnered", label="是否合作", lookup_expr="exact")

    @staticmethod
    @query_debugger
    def filter_availability_date(queryset: QuerySet["Instructor"], name: str, start_date: datetime.date):
        instructor_ids: List = []
        end_date: datetime.date = start_date + datetime.timedelta(days=global_constants.CLASS_DAYS - 1)

        # 解除合作的讲师不考虑可预约时间
        queryset = queryset.filter(is_partnered=True)

        # 没有任何时间的讲师一定可以预约
        event_instructor_ids = Event.objects.filter(
            Q(start_date__lte=end_date) & (Q(end_date__gte=start_date) | Q(end_date__isnull=True))
        ).values_list("instructor_id", flat=True)
        for instructor in queryset:
            if instructor.id not in event_instructor_ids:
                instructor_ids.append(instructor.id)
                continue

            if EventHandler.is_instructor_idle(
                    instructor=instructor,
                    start_date=start_date,
                    end_date=end_date
            ):
                instructor_ids.append(instructor.id)

        return queryset.filter(id__in=instructor_ids)

    @staticmethod
    def filter_course_id(queryset: QuerySet["Instructor"], name: str, course_id: Decimal):
        try:
            return queryset.filter(teachable_courses__contains=[int(course_id)])

        except (CourseTemplate.DoesNotExist, CourseTemplate.MultipleObjectsReturned):
            return queryset


class InstructorTaughtCoursesFilterClass(BaseFilterSet):
    name = PropertyFilter("name", label="培训班名称")
    target_client_company_name = PropertyFilter("target_client_company_name", label="客户公司")
    start_date = django_filters.DateFromToRangeFilter("start_date", label="开课时间")
