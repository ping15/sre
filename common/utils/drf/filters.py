import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


class PropertyFilter(django_filters.CharFilter):
    """
    Property属性筛选

    @property
    def value(self):
        return 1
    """
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


# class ForeignFilter(django_filters.Filter):
#     def __init__(self, model, source_field_name, target_field_name, *args, **kwargs):
#         self.model = model
#         self.source_field_name = source_field_name
#         self.target_field_name = target_field_name
#         super().__init__(*args, **kwargs)
#
#     def filter(self, queryset, value):
#         if not value:
#             return queryset
#
#         try:
#             instance = self.model.objects.get(id=value)
#             filter_criteria = {
#                 self.source_field_name: getattr(instance, self.target_field_name)
#             }
#             return queryset.filter(**filter_criteria)
#         except self.model.DoesNotExist:
#             return queryset.none()
#
#     # client_company_id = django_filters.NumberFilter(method='filter_by_client_company_id')
#
#     # class Meta:
#     #     model = YourModel
#     #     fields = ['client_company_id']
#     #
#     # def filter_by_client_company_id(self, queryset, name, value):
#     #     try:
#     #         client_company = ClientCompany.objects.get(id=value)
#     #         return queryset.filter(target_client_company_name=client_company.name)
#     #     except ClientCompany.DoesNotExist:
#     #         return queryset.none()  # 如果没有找到对应的客户公司，则返回空查询集


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """
    数字筛选器

    1,2,3,4 -> [1, 2, 3, 4]
    """
    pass


class BaseFilterSet(django_filters.FilterSet):
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


class DynamicRangeFilter(django_filters.Filter):
    """
    数字筛选器

    1-2 -> [1, 2]
    """
    def __init__(self, field_name=None, *args, **kwargs):
        self.field_name = field_name
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value or not self.field_name:
            return qs
        try:
            min_val, max_val = map(float, value.split('-'))
            filter_kwargs = {
                f"{self.field_name}__gte": min_val,
                f"{self.field_name}__lte": max_val
            }
            return qs.filter(Q(**filter_kwargs))
        except ValueError:
            return qs
