import django_filters

from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class TrainingClassFilterClass(BaseFilterSet):
    name = PropertyFilter("name", lookup_expr="icontains")
    instructor_name = PropertyFilter("instructor_name", lookup_expr="icontains")
    target_client_company = django_filters.NumberFilter("target_client_company_id")
