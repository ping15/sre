import django_filters

from common.utils.drf.filters import BaseFilterSet


class ClientCompanyFilterClass(BaseFilterSet):
    name = django_filters.CharFilter("name", lookup_expr="icontains")
    contact_email = django_filters.CharFilter("contact_email", lookup_expr="icontains")
    affiliated_manage_company_name = django_filters.CharFilter(
        "affiliated_manage_company_name", lookup_expr="icontains"
    )
