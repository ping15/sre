import django_filters

from common.utils.drf.filters import BaseFilterSet


class ManagementCompanyFilterClass(BaseFilterSet):
    name = django_filters.CharFilter("name", lookup_expr="icontains")
    email = django_filters.CharFilter("email", lookup_expr="icontains")
