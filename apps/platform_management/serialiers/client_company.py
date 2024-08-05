from typing import List

from rest_framework import serializers

from apps.platform_management.models import ClientCompany, ManageCompany
from common.utils.drf.serializer_validator import BasicSerializerValidator


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


class ClientCompanyCreateSerializer(
    serializers.ModelSerializer, BasicSerializerValidator
):
    class Meta:
        model = ClientCompany
        fields = "__all__"
