import datetime
from typing import List

import django_filters

from apps.my_lectures.handles.event import EventHandler
from apps.platform_management.models import Event
from common.utils import global_constants
from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class InstructorFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username", lookup_expr="icontains")
    introduction = django_filters.CharFilter("introduction", lookup_expr="icontains")
    satisfaction_score = django_filters.RangeFilter("satisfaction_score")
    city = django_filters.CharFilter("city", lookup_expr="exact")
    availability_date = django_filters.DateFilter(method="filter_availability_date")

    def filter_availability_date(self, queryset, name, today):
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


class InstructorTaughtCoursesFilterClass(BaseFilterSet):
    name = PropertyFilter("name")
    target_client_company_name = django_filters.CharFilter(
        "target_client_company_name", lookup_expr="icontains"
    )
    start_date = django_filters.DateFromToRangeFilter("start_date")
