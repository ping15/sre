from rest_framework import serializers

from apps.platform_management.models import ClientCompany


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


class ClientCompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientCompany
        fields = "__all__"


class ClientCompanyRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientCompany
        fields = "__all__"
