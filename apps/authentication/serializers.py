from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    captcha_text = serializers.CharField()
