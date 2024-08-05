from rest_framework import serializers

from apps.platform_management.models import Administrator, ManageCompany
from common.utils.drf.serializer_validator import BasicSerializerValidator


class AdministratorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "affiliated_manage_company_name",
            "role",
        ]


class AdministratorCreateSerializer(
    serializers.ModelSerializer, BasicSerializerValidator
):
    class Meta:
        model = Administrator
        exclude = ["password"]
