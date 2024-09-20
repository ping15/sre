import django_filters

from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class AllClassesFilterClass(BaseFilterSet):
    target_client_company_name = PropertyFilter("target_client_company_name", lookup_expr="icontains")
    location = django_filters.CharFilter("location", lookup_expr="icontains")
    name = PropertyFilter("name", lookup_expr="icontains")
    instructor_name = PropertyFilter("instructor_name", lookup_expr="icontains")
    affiliated_manage_company_name = PropertyFilter("affiliated_manage_company_name", lookup_expr="icontains")
    start_date = django_filters.DateFromToRangeFilter(field_name="start_date")
