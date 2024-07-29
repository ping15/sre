import django_filters
from django.db.models import F
from django_filters import rest_framework as filters


class BaseFilterSet(django_filters.FilterSet):
    @classmethod
    def setup_custom_filters(
        cls,
        model,
        fuzzy_filter_fields=None,
        time_filter_fields=None,
        property_fuzzy_filter_fields=None,
    ):
        if fuzzy_filter_fields:
            for field in fuzzy_filter_fields:
                cls.base_filters[field] = django_filters.CharFilter(
                    field_name=field, lookup_expr="icontains"
                )
        if time_filter_fields:
            for field in time_filter_fields:
                cls.base_filters[field] = django_filters.DateFilter(
                    field_name=field, lookup_expr="gte"
                )
                cls.base_filters[field + "_end"] = django_filters.DateFilter(
                    field_name=field, lookup_expr="lte"
                )
        if property_fuzzy_filter_fields:
            for field in property_fuzzy_filter_fields:
                cls.base_filters[field] = django_filters.CharFilter(
                    method=cls.filter_property(field), lookup_expr="icontains"
                )

    @classmethod
    def filter_property(cls, property_name):
        def _filter(queryset, name, value):
            if property_name == "instructor_name":
                pass
            return queryset

        return _filter


class MyModelFilterSet(BaseFilterSet):
    class Meta:
        model = None  # This should be overridden by each specific filter set
        fields = []
