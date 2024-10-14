import django_filters

from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class TrainingClassFilterClass(BaseFilterSet):
    name = PropertyFilter("name", label="培训班名称")
    instructor_name = PropertyFilter("instructor_name", label="讲师名称")
    target_client_company = django_filters.NumberFilter("target_client_company_id", lookup_expr="exact", label="客户公司")
