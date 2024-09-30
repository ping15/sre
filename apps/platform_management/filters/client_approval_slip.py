import django_filters

from common.utils.drf.filters import BaseFilterSet


class ClientApprovalSlipFilterClass(BaseFilterSet):
    id = django_filters.NumberFilter("id")
    affiliated_manage_company_name = django_filters.CharFilter("affiliated_manage_company_name")
    affiliated_client_company_name = django_filters.CharFilter("affiliated_client_company_name")
    submitter = django_filters.CharFilter("submitter")
    status = django_filters.CharFilter("status")
    submission_datetime = django_filters.DateTimeFromToRangeFilter("submission_datetime")
