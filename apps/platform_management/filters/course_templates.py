import django_filters

from common.utils.drf.filters import BaseFilterSet


class CourseTemplatesFilterClass(BaseFilterSet):
    name = django_filters.CharFilter("name", lookup_expr="icontains")
    course_overview = django_filters.CharFilter(
        "course_overview", lookup_expr="icontains"
    )
