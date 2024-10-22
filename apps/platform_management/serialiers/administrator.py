from rest_framework import serializers

from apps.platform_management.models import Administrator, ManageCompany
from common.utils import global_constants
from common.utils.drf.serializer_fields import ChoiceField, UniqueCharField
from common.utils.drf.serializer_validator import (
    BasicSerializerValidator,
    PhoneCreateSerializerValidator,
)
from common.utils.tools import reverse_dict


class AdministratorListSerializer(serializers.ModelSerializer):
    affiliated_manage_company_name = serializers.CharField(
        label="管理公司名字", source="affiliated_manage_company.name", read_only=True
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


class AdministratorCreateSerializer(serializers.ModelSerializer, PhoneCreateSerializerValidator):
    phone = UniqueCharField(label="管理员手机号码", max_length=16)
    role = ChoiceField(label="管理员角色", choices=Administrator.Role.choices)

    def validate(self, attrs):
        affiliated_manage_company: ManageCompany = attrs["affiliated_manage_company"]
        role: str = attrs["role"]
        default_manage_company: str = global_constants.DEFAULT_MANAGE_COMPANY

        # 公司选择[鸿雪公司]时角色不能选择[合作伙伴管理员]
        # 公司选择非[鸿雪公司]时角色不能选择[鸿雪公司管理员]
        if affiliated_manage_company.name == default_manage_company and role == Administrator.Role.PARTNER_MANAGER:
            raise serializers.ValidationError(f"公司选择[{default_manage_company}]时角色不能选择[合作伙伴管理员]")
        elif affiliated_manage_company.name != default_manage_company and role == Administrator.Role.COMPANY_MANAGER:
            raise serializers.ValidationError(f"公司选择非[{default_manage_company}]时角色不能选择[鸿雪公司管理员]")

        return super().validate(attrs)

    class Meta:
        model = Administrator
        exclude = ["password"]


class AdministratorUpdateSerializer(BasicSerializerValidator, AdministratorCreateSerializer):
    phone = serializers.CharField(label="管理员手机号", max_length=16)
    role = ChoiceField(label="管理员角色", choices=Administrator.Role.choices)

    def save(self, **kwargs):
        if not self.initial_data["phone"] == self.instance.phone:
            PhoneCreateSerializerValidator.validate_phone(self.initial_data["phone"])
        super().save(**kwargs)

    class Meta:
        model = Administrator
        exclude = ["password"]


class AdministratorBatchImportSerializer(serializers.ModelSerializer, PhoneCreateSerializerValidator):
    phone = UniqueCharField(label="管理员手机号码", max_length=16)

    def to_internal_value(self, data):
        data["role"] = reverse_dict(dict(Administrator.Role.choices)).get(data["role"])
        try:
            data["affiliated_manage_company"] = ManageCompany.objects.get(
                name=data["affiliated_manage_company_name"]).id
        except ManageCompany.DoesNotExist:
            raise serializers.ValidationError(f"该管理公司不存在: {data['affiliated_manage_company_name']}")
        super().to_internal_value(data)
        return data

    class Meta:
        model = Administrator
        exclude = ["password"]
