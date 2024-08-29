from rest_framework import serializers

from apps.platform_management.models import Administrator, ManageCompany
from common.utils.drf.serializer_fields import ChoiceField
from common.utils.drf.serializer_validator import (
    BasicSerializerValidator,
    PhoneCreateSerializerValidator,
)
from common.utils.tools import reverse_dict


class AdministratorListSerializer(serializers.ModelSerializer):
    affiliated_manage_company_name = serializers.CharField(source="affiliated_manage_company.name", read_only=True)

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


class AdministratorCreateSerializer(serializers.ModelSerializer, PhoneCreateSerializerValidator):
    role = ChoiceField(choices=Administrator.Role.choices)

    class Meta:
        model = Administrator
        exclude = ["password"]


class AdministratorUpdateSerializer(serializers.ModelSerializer, BasicSerializerValidator):
    role = ChoiceField(choices=Administrator.Role.choices)

    def save(self, **kwargs):
        if not self.initial_data["phone"] == self.instance.phone:
            PhoneCreateSerializerValidator.validate_phone(self.initial_data["phone"])
        super().save(**kwargs)

    class Meta:
        model = Administrator
        exclude = ["password"]


class AdministratorBatchImportSerializer(serializers.ModelSerializer, PhoneCreateSerializerValidator):
    def to_internal_value(self, data):
        data["role"] = reverse_dict(dict(Administrator.Role.choices)).get(data["role"])

        try:
            data["affiliated_manage_company"] = ManageCompany.objects.get(
                name=data["affiliated_manage_company_name"]).id
        except ManageCompany.DoesNotExist:
            raise serializers.ValidationError(
                f"该管理公司不存在: {data['affiliated_manage_company_name']}"
            )
        # return super().to_internal_value(data)
        return data

    class Meta:
        model = Administrator
        exclude = ["password"]
