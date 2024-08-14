import django_filters

from common.utils.drf.filters import BaseFilterSet


class ClientStudentFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username", lookup_expr="icontains")
    affiliated_client_company_name = django_filters.CharFilter(
        "affiliated_client_company_name", lookup_expr="icontains"
    )
    affiliated_client_company_name__exact = django_filters.CharFilter(
        "affiliated_client_company_name", lookup_expr="exact"
    )
    affiliated_manage_company_name = django_filters.CharFilter(
        "affiliated_manage_company_name", lookup_expr="icontains"
    )
    email = django_filters.CharFilter("email", lookup_expr="icontains")
    phone = django_filters.CharFilter("phone", lookup_expr="icontains")
