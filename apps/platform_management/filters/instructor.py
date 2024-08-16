import django_filters

from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class InstructorFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username", lookup_expr="icontains")
    introduction = django_filters.CharFilter("introduction", lookup_expr="icontains")


class InstructorTaughtCoursesFilterClass(BaseFilterSet):
    name = PropertyFilter("name")
    target_client_company_name = django_filters.CharFilter(
        "target_client_company_name", lookup_expr="icontains"
    )
    start_date = django_filters.DateFromToRangeFilter("start_date")
