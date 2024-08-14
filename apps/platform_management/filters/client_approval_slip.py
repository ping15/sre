import django_filters

from common.utils.drf.filters import BaseFilterSet


class ClientApprovalSlipFilterClass(BaseFilterSet):
    id = django_filters.NumberFilter("id")
    affiliated_manage_company_name = django_filters.CharFilter(
        "affiliated_manage_company_name", lookup_expr="icontains"
    )
    affiliated_client_company_name = django_filters.CharFilter(
        "affiliated_client_company_name", lookup_expr="icontains"
    )
    submitter = django_filters.CharFilter(
        field_name="submitter", lookup_expr="icontains"
    )
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")
    submission_datetime = django_filters.DateTimeFromToRangeFilter(
        field_name="submission_datetime"
    )
