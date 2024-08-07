from rest_framework import serializers

from apps.platform_management.models import Administrator
from common.utils.drf.serializer_fields import ChoiceField
from common.utils.drf.serializer_validator import (
    PhoneCreateSerializerValidator,
    BasicSerializerValidator,
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
):
    role = ChoiceField(choices=Administrator.Role.choices)

    class Meta:
        model = Administrator
        exclude = ["password"]


class AdministratorUpdateSerializer(
    serializers.ModelSerializer,
    BasicSerializerValidator,
):
    role = ChoiceField(choices=Administrator.Role.choices)

    def save(self, **kwargs):
        if not self.initial_data["phone"] == self.instance.phone:
            PhoneCreateSerializerValidator.validate_phone(self.initial_data["phone"])
        super().save(**kwargs)

    class Meta:
        model = Administrator
        exclude = ["password"]


class AdministratorBatchImportSerializer:
    pass
