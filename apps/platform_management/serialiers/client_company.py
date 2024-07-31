from typing import List

from rest_framework import serializers

from apps.platform_management.models import ClientCompany, ManageCompany


class ClientCompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientCompany
        fields = [
            "id",
            "name",
            "contact_email",
            "affiliated_manage_company_name",
            "student_count",
        ]


class ClientCompanyRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientCompany
        fields = "__all__"


class ClientCompanyCreateSerializer(serializers.ModelSerializer):
    affiliated_manage_company_name = serializers.ChoiceField(
        choices=[(name, name) for name in ManageCompany.names],
        error_messages={"invalid_choice": f"该管理公司不存在, 可选管理公司: {ClientCompany.names}"},
    )

    class Meta:
        model = ClientCompany
        fields = "__all__"
