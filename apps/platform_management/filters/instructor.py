import datetime
from typing import List

import django_filters
from django.db.models import QuerySet

from apps.my_lectures.handles.event import EventHandler
from apps.platform_management.models import CourseTemplate, Event, Instructor
from common.utils import global_constants
from common.utils.drf.filters import BaseFilterSet, DynamicRangeFilter, PropertyFilter


class InstructorFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username", lookup_expr="icontains", label="讲师名称")
    introduction = django_filters.CharFilter("introduction", lookup_expr="icontains", label="简介")
    satisfaction_score = DynamicRangeFilter(field_name="satisfaction_score", label="讲师评分")
    city = django_filters.CharFilter("city", lookup_expr="exact", label="城市")
    availability_date = django_filters.DateFilter(method="filter_availability_date", label="可预约时间")
    course_id = django_filters.NumberFilter(method="filter_course_id", label="培训班授课课程id")
    is_partnered = django_filters.BooleanFilter("is_partnered", label="是否合作")

    def filter_availability_date(self, queryset: QuerySet["Instructor"], name: str, today: datetime.date):
        if not self.request.user.role == global_constants.Role.INSTRUCTOR.value:
            return queryset

        # 当 今天可用 + 明天可用 时，这个讲师可以预约
        today_can_use = tomorrow_can_use = False
        tomorrow = today + datetime.timedelta(days=1)
        cancel_events: List[datetime.date] = Event.objects.filter(
            event_type=Event.EventType.CANCEL_UNAVAILABILITY).values_list("start_date", flat=True)
        instructor_ids: List = []
        for instructor in queryset:
            if EventHandler.is_current_date_in_cancel_events(today, cancel_events):
                today_can_use = True

            if EventHandler.is_current_date_in_cancel_events(tomorrow, cancel_events):
                tomorrow_can_use = True

            if today_can_use and tomorrow_can_use:
                instructor_ids.append(instructor.id)
                continue

            for rule in instructor.events.filter(event_type__in=Event.EventType.rule_types):
                if not EventHandler.is_current_date_in_rule(today, rule):
                    today_can_use = True

                if not EventHandler.is_current_date_in_rule(tomorrow, rule):
                    tomorrow_can_use = True

            if today_can_use and tomorrow_can_use:
                instructor_ids.append(instructor.id)
                continue

        return queryset.filter(id__in=instructor_ids)

    def filter_course_id(self, queryset: QuerySet["Instructor"], name: str, course_id: int):
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
