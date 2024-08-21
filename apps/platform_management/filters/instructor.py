from typing import List

import django_filters
from django.db.models import QuerySet

from apps.platform_management.models import Event
from common.utils import global_constants
from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class InstructorFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username", lookup_expr="icontains")
    introduction = django_filters.CharFilter("introduction", lookup_expr="icontains")
    satisfaction_score = django_filters.RangeFilter("satisfaction_score")
    city = django_filters.CharFilter("city", lookup_expr="exact")
    availability_date = django_filters.DateFilter(method="filter_availability_date")

    def filter_availability_date(self, queryset, name, value):
        if not self.request.user.role == global_constants.Role.INSTRUCTOR.value:
            return queryset

        instructor_ids: List = []
        for instructor in queryset:
            rules: QuerySet["Event"] = instructor.events.filter(event_type__in=[
                Event.EventType.RECURRING_UNAVAILABILITY.value, Event.EventType.ONE_TIME_UNAVAILABILITY.value
            ])
            for rule in rules:
                pass

        return queryset.filter(id__in=instructor_ids)


class InstructorTaughtCoursesFilterClass(BaseFilterSet):
    name = PropertyFilter("name")
    target_client_company_name = django_filters.CharFilter(
        "target_client_company_name", lookup_expr="icontains"
    )
    start_date = django_filters.DateFromToRangeFilter("start_date")
