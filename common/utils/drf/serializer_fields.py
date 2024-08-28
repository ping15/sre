from datetime import datetime
from enum import Enum

from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from common.utils.cipher import cipher
from common.utils.tools import reverse_dict


class PasswordField(serializers.CharField):
    def to_internal_value(self, data):
        return cipher.encrypt(str(data))

    def to_representation(self, data):
        return cipher.decrypt(str(data))


class ChoiceField(serializers.ChoiceField):
    default_error_messages = {
        "invalid_choice": "{input} is not a valid choice, choices: {choices}"
    }

    def to_internal_value(self, data):
        data = reverse_dict(self.choices).get(data, data)
        if data == "" and self.allow_blank:
            return ""
        if isinstance(data, Enum) and str(data) != str(data.value):
            data = data.value
        try:
            return self.choice_strings_to_values[str(data)]
        except KeyError:
            self.fail("invalid_choice", input=data, choices=list(self.choices.keys()))

    # def to_representation(self, value):
    #     return super().to_representation(self.choices.get(value))


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
