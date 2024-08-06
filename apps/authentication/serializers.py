from rest_framework import serializers

from common.utils.drf.serializer_validator import BasicSerializerValidator


class LoginSerializer(serializers.Serializer, BasicSerializerValidator):
    phone = serializers.CharField()
    captcha_text = serializers.CharField()


class SMSSerializer(serializers.Serializer, BasicSerializerValidator):
    phone = serializers.CharField()
