from rest_framework import serializers

from apps.platform_management.models import Administrator
from common.utils.drf.serializer_fields import ChoiceField
from common.utils.drf.serializer_validator import (
    PhoneCreateSerializerValidator,
)


class AdministratorListSerializer(serializers.ModelSerializer):
    affiliated_manage_company_name = serializers.CharField(
        source="affiliated_manage_company.name", read_only=True
    )

    class Meta:
        model = Administrator
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "affiliated_manage_company_name",
            "affiliated_manage_company",
            "role",
        ]


class AdministratorCreateSerializer(
    serializers.ModelSerializer,
    PhoneCreateSerializerValidator,
    # BasicSerializerValidator,
):
    role = ChoiceField(choices=Administrator.Role.choices)

    class Meta:
        model = Administrator
        exclude = ["password"]
