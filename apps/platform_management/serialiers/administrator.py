from rest_framework import serializers

from apps.platform_management.models import Administrator
from common.utils.drf.serializer_fields import ChoiceField
from common.utils.drf.serializer_validator import (
    BasicSerializerValidator,
    PhoneCreateSerializerValidator,
)


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
    serializers.ModelSerializer,
    PhoneCreateSerializerValidator,
    BasicSerializerValidator,
):
    role = ChoiceField(choices=Administrator.Role.choices)

    class Meta:
        model = Administrator
        exclude = ["password"]
