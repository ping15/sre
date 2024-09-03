import django_filters
from django.db.models import QuerySet

from apps.my_lectures.models import InstructorEvent
from common.utils.drf.filters import BaseFilterSet


class InstructorEventFilterClass(BaseFilterSet):
    event_name = django_filters.CharFilter("event_name", lookup_expr="icontains")
    initiator = django_filters.CharFilter("initiator", lookup_expr="icontains")
    status = django_filters.CharFilter("status", lookup_expr="exact")
    created_datetime = django_filters.DateTimeFromToRangeFilter("created_datetime")

    is_completed = django_filters.BooleanFilter(method="filter_is_completed")

    def filter_is_completed(self, queryset: QuerySet["InstructorEvent"], name: str, is_completed: bool):
        if is_completed:
            return queryset.filter(status__in=InstructorEvent.Status.get_completed_statuses())

        return queryset.filter(status__in=InstructorEvent.Status.get_pending_statuses())
