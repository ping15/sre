import django_filters

from apps.platform_management.models import ClientCompany
from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class ClientStudentFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username", lookup_expr="icontains")
    affiliated_client_company = django_filters.NumberFilter(method="filter_affiliated_client_company")
    affiliated_client_company_name = django_filters.CharFilter(
        "affiliated_client_company_name", lookup_expr="icontains"
    )
    # affiliated_client_company_name__exact = django_filters.CharFilter(
    #     "affiliated_client_company_name", lookup_expr="exact"
    # )
    affiliated_manage_company_name = PropertyFilter(
        "affiliated_manage_company_name", lookup_expr="icontains"
    )
    email = django_filters.CharFilter("email", lookup_expr="icontains")
    phone = django_filters.CharFilter("phone", lookup_expr="icontains")
    department = django_filters.CharFilter("department", lookup_expr="icontains")
    position = django_filters.CharFilter("position", lookup_expr="icontains")

    def filter_affiliated_client_company(self, queryset, name, value):
        return self._filter_by_related_model(
            queryset, value, ClientCompany, "affiliated_client_company_name", "name"
        )
