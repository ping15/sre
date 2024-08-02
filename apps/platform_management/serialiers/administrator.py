from rest_framework import serializers

from apps.platform_management.models import Administrator, ManageCompany
from common.utils.drf.serializer_fields import PasswordField
from common.utils.drf.serializer_validator import BasicSerializerValidator


class AdministratorListSerializer(serializers.ModelSerializer):
    password = PasswordField()

    class Meta:
        model = Administrator
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "password",
            "affiliated_manage_company_name",
            "role",
        ]


class AdministratorCreateSerializer(
    serializers.ModelSerializer, BasicSerializerValidator
):
    password = PasswordField()
    affiliated_manage_company_name = serializers.ChoiceField(
        choices=[(name, name) for name in ManageCompany.names],
        error_messages={"invalid_choice": f"该管理公司不存在, 可选管理公司: {ManageCompany.names}"},
    )

    class Meta:
        model = Administrator
        fields = "__all__"
