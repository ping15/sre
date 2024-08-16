from collections import OrderedDict

import django_filters
from django.core.exceptions import ObjectDoesNotExist


class PropertyFilter(django_filters.CharFilter):
    def filter(self, qs, value):
        if self.lookup_expr == "icontains":
            return qs.filter(
                id__in=[
                    instance.id
                    for instance in qs
                    if value.lower() in getattr(instance, self.field_name).lower()
                ]
            )

        return qs


class ForeignFilter(django_filters.Filter):
    def __init__(self, model, source_field_name, target_field_name, *args, **kwargs):
        self.model = model
        self.source_field_name = source_field_name
        self.target_field_name = target_field_name
        super().__init__(*args, **kwargs)

    def filter(self, queryset, value):
        if not value:
            return queryset

        try:
            instance = self.model.objects.get(id=value)
            filter_criteria = {
                self.source_field_name: getattr(instance, self.target_field_name)
            }
            return queryset.filter(**filter_criteria)
        except self.model.DoesNotExist:
            return queryset.none()

    # client_company_id = django_filters.NumberFilter(method='filter_by_client_company_id')

    # class Meta:
    #     model = YourModel
    #     fields = ['client_company_id']
    #
    # def filter_by_client_company_id(self, queryset, name, value):
    #     try:
    #         client_company = ClientCompany.objects.get(id=value)
    #         return queryset.filter(target_client_company_name=client_company.name)
    #     except ClientCompany.DoesNotExist:
    #         return queryset.none()  # 如果没有找到对应的客户公司，则返回空查询集


class BaseFilterSet(django_filters.FilterSet):
    # @classmethod
    # def add_filters(
    #     cls, filter_set, filter_fields, filter_class, lookup_exprs, add_prefix
    # ):
    #     for field in filter_fields:
    #         for lookup_expr in lookup_exprs:
    #             filter_instance = filter_class(
    #                 field_name=field, lookup_expr=lookup_expr
    #             )
    #             filter_set.base_filters[
    #                 field + (f"_{lookup_expr}" if add_prefix else "")
    #             ] = filter_instance
    #
    # @classmethod
    # def setup_filters(
    #     cls,
    #     model,
    #     string_fuzzy_filter_fields=None,
    #     time_filter_fields=None,
    #     property_fuzzy_filter_fields=None,
    #     datetime_filter_fields=None,
    #     integer_filter_fields=None,
    # ):
    #     cls.base_filters = OrderedDict()
    #
    #     filter_mappings = [
    #         (
    #             string_fuzzy_filter_fields or [],
    #             django_filters.CharFilter,
    #             ["icontains"],
    #             False,
    #         ),
    #         (
    #             time_filter_fields or [],
    #             django_filters.DateFilter,
    #             ["gte", "gt", "lte", "lt"],
    #             True,
    #         ),
    #         (
    #             datetime_filter_fields or [],
    #             django_filters.DateTimeFilter,
    #             ["gte", "gt", "lte", "lt"],
    #             True,
    #         ),
    #         (property_fuzzy_filter_fields or [], PropertyFilter, ["icontains"], False),
    #         (
    #             integer_filter_fields or [],
    #             django_filters.NumberFilter,
    #             ["exact"],
    #             False,
    #         ),
    #     ]
    #
    #     for filter_fields, filter_class, lookup_exprs, add_prefix in filter_mappings:
    #         if filter_fields:
    #             cls.add_filters(
    #                 cls, filter_fields, filter_class, lookup_exprs, add_prefix
    #             )

    @classmethod
    def _filter_by_related_model(cls, queryset, pk, model, field_name, related_field):
        """
        1. 从B Model中获取id为pk的实例，获取related_field的值
        2. 再从queryset中筛选字段field_name为上一步获取的值
        """
        try:
            related_instance = model.objects.get(id=pk)
            filter_value = getattr(related_instance, related_field)
            return queryset.filter(**{field_name: filter_value})
        except ObjectDoesNotExist:
            return queryset.none()

    # @classmethod
    # def add_filter_with_lookups(cls, field_name, filter_type, lookup_exprs):
    #     # 添加带有查找表达式的过滤器
    #     for lookup_expr in lookup_exprs:
    #         lookup_field_name = f"{field_name}_{lookup_expr}"
    #         cls.base_filters[lookup_field_name] = filter_type(
    #             field_name=field_name, lookup_expr=lookup_expr
    #         )
    #
    # @classmethod
    # def build_filter(cls, field_name, filter_type):
    #     lookup_exprs = ["gte", "gt", "lte", "lt"]
    #     cls.add_filter_with_lookups(field_name, filter_type, lookup_exprs)

    # @classmethod
    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)
    #     # 在子类初始化时设置过滤器
    #     for field_name, filter_instance in cls.declared_filters.items():
    #         if isinstance(filter_instance, (django_filters.DateTimeFilter, django_filters.DateFilter)):
    #             cls.build_filter(field_name, type(filter_instance))
