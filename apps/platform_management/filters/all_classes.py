import django_filters

from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class AllClassesFilterClass(BaseFilterSet):
    name = PropertyFilter("name", lookup_expr="icontains")
    instructor_name = PropertyFilter("instructor_name", lookup_expr="icontains")
    affiliated_manage_company_name = PropertyFilter(
        "affiliated_manage_company_name", lookup_expr="icontains"
    )
    start_date = django_filters.DateFromToRangeFilter(field_name="start_date")
