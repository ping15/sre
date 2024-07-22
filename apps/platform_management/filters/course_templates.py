import django_filters
from django.db.models import Case, When, IntegerField
from rest_framework.filters import OrderingFilter

from apps.platform_management.models import CourseTemplate


class CourseTemplateFilterClass(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    course_overview = django_filters.CharFilter(
        field_name="course_overview", lookup_expr="icontains"
    )

    class Meta:
        model = CourseTemplate
        fields = ["name", "course_overview"]


class CourseTemplateOrderingFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering_fields = self.get_ordering(request, queryset, view)
        if not ordering_fields:
            return queryset

        my_ordering = []
        for field in ordering_fields:
            reverse = field.startswith("-")
            if field.lstrip("-") == "status":
                status_ordering_rule = (
                    CourseTemplate.STATUS_ORDERING_RULE
                    if not reverse
                    else [
                        (field, score)
                        for score, (field, _) in enumerate(
                            CourseTemplate.STATUS_ORDERING_RULE
                        )
                    ]
                )
                my_ordering.append(
                    Case(
                        *[
                            When(status=status, then=value)
                            for status, value in status_ordering_rule
                        ],
                        output_field=IntegerField()
                    )
                )
            else:
                my_ordering.append(field)

        return queryset.order_by(*my_ordering)
