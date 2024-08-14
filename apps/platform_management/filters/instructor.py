import django_filters

from common.utils.drf.filters import BaseFilterSet, PropertyFilter


class InstructorFilterClass(BaseFilterSet):
    username = django_filters.CharFilter("username", lookup_expr="icontains")
    introduction = django_filters.CharFilter("introduction", lookup_expr="icontains")


# self.filter_class.setup_filters(
#             TrainingClass,
#             property_fuzzy_filter_fields=["name"],
#             string_fuzzy_filter_fields=["target_client_company_name"],
#             time_filter_fields=["start_date"],
#         )
class InstructorTaughtCoursesFilterClass(BaseFilterSet):
    name = PropertyFilter("name")
    target_client_company_name = django_filters.CharFilter(
        "target_client_company_name", lookup_expr="icontains"
    )
    start_date = django_filters.DateFromToRangeFilter("start_date")
