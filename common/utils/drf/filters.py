import django_filters
from django.db.models import F
from django_filters import rest_framework as filters


class PropertyFilter(django_filters.CharFilter):
    def filter(self, qs, value):
        if self.lookup_expr == "icontains":
            return qs.filter(
                id__in=[
                    instance.id
                    for instance in qs
                    if value in getattr(instance, self.field_name).lower()
                ]
            )

        return qs


class BaseFilterSet(django_filters.FilterSet):
    @classmethod
    def add_filters(
        cls, filter_class, filter_fields, filter_type, lookup_exprs, add_prefix
    ):
        for field in filter_fields:
            for lookup_expr in lookup_exprs:
                filter_instance = filter_type(field_name=field, lookup_expr=lookup_expr)
                filter_class.base_filters[
                    field + (f"_{lookup_expr}" if add_prefix else "")
                ] = filter_instance

    @classmethod
    def setup_filters(
        cls,
        model,
        fuzzy_filter_fields=None,
        time_filter_fields=None,
        property_fuzzy_filter_fields=None,
        datetime_filter_fields=None,
        integer_filter_fields=None,
    ):
        filter_mappings = [
            (
                fuzzy_filter_fields or [],
                django_filters.CharFilter,
                ["icontains"],
                False,
            ),
            (
                time_filter_fields or [],
                django_filters.DateFilter,
                ["gte", "gt", "lte", "lt"],
                True,
            ),
            (
                datetime_filter_fields or [],
                django_filters.DateTimeFilter,
                ["gte", "gt", "lte", "lt"],
                True,
            ),
            (property_fuzzy_filter_fields or [], PropertyFilter, ["icontains"], False),
            (
                integer_filter_fields or [],
                django_filters.NumberFilter,
                ["exact"],
                False,
            ),
        ]

        for filter_fields, filter_type, lookup_exprs, add_prefix in filter_mappings:
            if filter_fields:
                cls.add_filters(
                    cls, filter_fields, filter_type, lookup_exprs, add_prefix
                )

        # # 模糊匹配字段列表
        # if fuzzy_filter_fields:
        #     for field in fuzzy_filter_fields:
        #         cls.base_filters[field] = django_filters.CharFilter(
        #             field_name=field, lookup_expr="icontains"
        #         )
        #
        # # time匹配字段列表
        # if time_filter_fields:
        #     for field in time_filter_fields:
        #         for lookup_expr in ["gte", "gt", "lte", "lt"]:
        #             cls.base_filters[field + f"_{lookup_expr}"] = django_filters.DateFilter(
        #                 field_name=field, lookup_expr=lookup_expr
        #             )
        #
        # # datetime匹配字段列表
        # if datetime_filter_fields:
        #     for field in datetime_filter_fields:
        #         for lookup_expr in ["gte", "gt", "lte", "lt"]:
        #             cls.base_filters[field + f"_{lookup_expr}"] = django_filters.DateTimeFilter(
        #                 field_name=field, lookup_expr="icontains"
        #             )
        #
        # # property模糊匹配字段列表
        # if property_fuzzy_filter_fields:
        #     for field in property_fuzzy_filter_fields:
        #         cls.base_filters[field] = PropertyFilter(
        #             field_name=field, lookup_expr="icontains"
        #         )
