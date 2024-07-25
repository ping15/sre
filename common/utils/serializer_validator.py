import re

from rest_framework import serializers


class BasicSerializerValidator:
    @classmethod
    def validate_phone(cls, value):
        """
        Validate phone number.
        Simple validation for phone number (example: 11 digits only).
        You can customize this as per your requirements.
        """
        pattern = re.compile(r"^1[35678]\d{9}$")
        if not pattern.match(value):
            raise serializers.ValidationError("手机号必须为11位，第一位为1，第二位可选数字[3,5,6,7,8]")
        return value
