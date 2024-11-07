import django_filters

from apps.platform_management.models import ClientCompany
from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class ClientStudentFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username")
    affiliated_client_company = django_filters.NumberFilter(method="filter_affiliated_client_company")
    affiliated_client_company_name = django_filters.CharFilter("affiliated_client_company_name")
    affiliated_manage_company_name = PropertyFilter("affiliated_manage_company_name")
    affiliated_manage_company = PropertyFilter("affiliated_manage_company_id", lookup_expr="exact")
    email = django_filters.CharFilter("email")
    phone = django_filters.CharFilter("phone")
    department = django_filters.CharFilter("department")
    position = django_filters.CharFilter("position")
    gender = django_filters.CharFilter("gender")
    id_number = django_filters.CharFilter("id_number")
    education = django_filters.CharFilter("education", lookup_expr="exact")

    def filter_affiliated_client_company(self, queryset, name, value):
        return self._filter_by_related_model(queryset, value, ClientCompany, "affiliated_client_company_name", "name")
