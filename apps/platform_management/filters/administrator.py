import django_filters

from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class AdministratorFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username", lookup_expr="icontains")
    email = django_filters.CharFilter("email", lookup_expr="icontains")
    phone = django_filters.CharFilter("phone", lookup_expr="icontains")
    affiliated_manage_company_name = PropertyFilter(
        "affiliated_manage_company_name", lookup_expr="icontains"
    )
    role = django_filters.CharFilter("role", lookup_expr="icontains")
