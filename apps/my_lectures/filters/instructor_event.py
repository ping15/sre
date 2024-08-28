import django_filters

from common.utils.drf.filters import BaseFilterSet


class InstructorEventFilterClass(BaseFilterSet):
    status = django_filters.CharFilter("status", lookup_expr="exact")
    status_not = django_filters.CharFilter("status", lookup_expr="exact", exclude=True)
