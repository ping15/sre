from rest_framework import serializers

from common.utils.cipher import cipher


class PasswordField(serializers.CharField):
    def to_internal_value(self, data):
        return cipher.encrypt(data)

    def to_representation(self, data):
        return cipher.decrypt(data)
