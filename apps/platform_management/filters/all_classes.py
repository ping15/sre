import django_filters

from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class AllClassesFilterClass(BaseFilterSet):
    target_client_company_name = PropertyFilter("target_client_company_name", label="客户公司名称")
    location = django_filters.CharFilter("location", label="开课地点")
    name = PropertyFilter("name", label="培训班名称")
    instructor_name = PropertyFilter("instructor_name", label="讲师名称")
    affiliated_manage_company_name = PropertyFilter("affiliated_manage_company_name", label="管理公司名称")
    start_date = django_filters.DateFromToRangeFilter("start_date", label="开课时间")
    target_client_company = django_filters.NumberFilter("target_client_company_id", label="客户公司id")
