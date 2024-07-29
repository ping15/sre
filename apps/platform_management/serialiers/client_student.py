from rest_framework import serializers

from apps.platform_management.models import ClientStudent, ClientCompany, ManageCompany


class ClientStudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStudent
        exclude = ["department", "position"]


class ClientStudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentQuickSearchSerializer(serializers.Serializer):
    class ClientCompanySerializer(serializers.Serializer):
        affiliated_client_company_name = serializers.CharField(source="name")

    manage_company_name = serializers.CharField(source="name")
    children = ClientCompanySerializer(source="client_companies", many=True)
