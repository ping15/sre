import django_filters

from apps.platform_management.models import ManageCompany
from common.utils.drf.filters import BaseFilterSet


class ClientCompanyFilterClass(BaseFilterSet):
    name = django_filters.CharFilter("name", lookup_expr="icontains")
    contact_email = django_filters.CharFilter("contact_email", lookup_expr="icontains")
    affiliated_manage_company_name = django_filters.CharFilter(
        "affiliated_manage_company_name", lookup_expr="icontains"
    )
    affiliated_manage_company = django_filters.NumberFilter(method="filter_affiliated_client_company")

    def filter_affiliated_client_company(self, queryset, name, value):
        return self._filter_by_related_model(
            queryset, value, ManageCompany, "affiliated_manage_company_name", "name"
        )
