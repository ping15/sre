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

        elif self.lookup_expr == "exact":
            return qs.filter(
                id__in=[
                    instance.id
                    for instance in qs
                    if value == str(getattr(instance, self.field_name))
                ]
            )

        return qs

    def get_q_object(self, qs, value):
        if self.lookup_expr == "icontains":
            matched_ids = [
                instance.id
                for instance in qs
                if value.lower() in getattr(instance, self.field_name).lower()
            ]
            return Q(id__in=matched_ids)
        return Q()


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """
    数字筛选器

    1,2,3,4 -> [1, 2, 3, 4]
    """
    pass


class BaseFilterSet(django_filters.FilterSet):
    default = django_filters.CharFilter(method="filter_default", label="默认筛选字段")

    def filter_default(self, queryset, name, value):
        # 获取所有需要匹配的字段和它们的类型
        search_fields = self.base_filters.copy()

        del search_fields["default"]

        # 获取模型的所有字段名称
        model_fields = {field.name for field in queryset.model._meta.get_fields()}

        # 构建 Q 对象进行 OR 查询
        query = Q()

        for field_name, filter_instance in search_fields.items():
            if isinstance(filter_instance, PropertyFilter):
                query |= filter_instance.get_q_object(queryset, value)
                continue

            # 检查字段是否是模型字段
            if field_name not in model_fields:
                continue

            if isinstance(filter_instance, django_filters.CharFilter):
                # 对字符串字段进行部分匹配
                query |= Q(**{f"{field_name}__icontains": value})
            elif isinstance(filter_instance, django_filters.NumberFilter):
                try:
                    # 尝试将 value 转换为数字
                    num_value = float(value)
                    query |= Q(**{f"{field_name}": num_value})
                except ValueError:
                    # 如果转换失败，跳过这个字段
                    continue

        return queryset.filter(query)

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
