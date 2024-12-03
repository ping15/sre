from datetime import datetime
from enum import Enum
from typing import Any, Type, TypeVar

from dateutil.relativedelta import relativedelta
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Model
from django.utils.html import escape
from rest_framework import serializers

from common.utils.cipher import cipher
from common.utils.file_defense import convert_resource_url
from common.utils.tools import reverse_dict

T = TypeVar(name="T", bound=Model)


class PasswordField(serializers.CharField):
    def to_internal_value(self, data):
        return cipher.encrypt(str(data))

    def to_representation(self, data):
        return cipher.decrypt(str(data))


class ChoiceField(serializers.ChoiceField):
    default_error_messages = {
        "invalid_choice": "{input} is not a valid choice, choices: {choices}"
    }

    def __init__(self, choices, mapping=None, **kwargs):
        super().__init__(choices, **kwargs)
        self.mapping = mapping or {}

    def to_internal_value(self, data):
        data = reverse_dict(self.choices).get(data, data)
        if data == "" and self.allow_blank:
            return None
        if data in self.mapping:
            return self.mapping[data]

        if isinstance(data, Enum) and str(data) != str(data.value):
            data = data.value
        try:
            return self.choice_strings_to_values[str(data)]
        except KeyError:
            self.fail("invalid_choice", input=data, choices=list(self.choices.keys()))


class MappingField(serializers.Field):
    def __init__(self, field, mapping=None, *args, **kwargs):
        self.field = field
        self.mapping = mapping or {}
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if data in self.mapping:
            return self.mapping[data]
        return self.field.to_internal_value(data)

    def to_representation(self, value):
        return self.field.to_representation(value)


class MonthYearField(serializers.Field):
    def __init__(self, *args, time_delta=relativedelta(), **kwargs):
        super().__init__(*args, **kwargs)
        self.time_delta = time_delta

    def to_internal_value(self, data):
        try:
            # 将传入的格式 'YYYY-MM' 转换为 datetime.date
            return datetime.strptime(data, '%Y-%m').date() + self.time_delta
        except ValueError:
            raise serializers.ValidationError("Date format should be 'YYYY-MM'")


class UniqueCharField(serializers.CharField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        # 检查外部序列化器是否是 ModelSerializer 的子类
        if not isinstance(self.parent, serializers.ModelSerializer):
            raise TypeError("UniqueCharField必须在ModelSerializer中使用.")

        model = self.parent.Meta.model
        if model.objects.filter(**{self.field_name: data}).exists():
            raise serializers.ValidationError(f"该{self.label or self.field_name}{data}已存在")

        return data


class ModelInstanceField(serializers.IntegerField):
    def __init__(self, model, field="id", **kwargs):
        self.model = model
        self.field = field
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return get_model_instance_or_raise(self.model, self.field, value)

    def to_representation(self, value):
        return value


class CleanedHTMLField(serializers.CharField):
    def to_internal_value(self, value):
        return super().to_internal_value(escape(value))

    def to_representation(self, value):
        return super().to_representation(value)


class ResourceURLField(serializers.CharField):
    def to_internal_value(self, value):
        return convert_resource_url(value)

    def to_representation(self, value):
        return convert_resource_url(value)


class ListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        child = kwargs.pop("child", None)

        if isinstance(child, dict):
            class ChildSerializer(serializers.Serializer):
                pass

            for key, field in child.items():
                ChildSerializer._declared_fields[key] = field
            child = ChildSerializer()

        kwargs["child"] = child
        super().__init__(*args, **kwargs)


def get_model_instance_or_raise(model: Type[T], field: str, value: Any) -> T:
    try:
        return model.objects.get(**{field: value})
    except ObjectDoesNotExist:
        raise serializers.ValidationError(f"该 {model.__name__} 模型实例查不到")
    except MultipleObjectsReturned:
        raise serializers.ValidationError(f"该 {model.__name__} 模型实例对象存在多个")
