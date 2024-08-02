from rest_framework import serializers

from common.utils.drf.serializer_fields import PasswordField


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = PasswordField()
