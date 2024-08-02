from rest_framework import serializers

from apps.platform_management.models import ClientStudent, ClientCompany
from common.utils.drf.serializer_fields import PasswordField


class ClientStudentListSerializer(serializers.ModelSerializer):
    password = PasswordField()

    class Meta:
        model = ClientStudent
        exclude = ["department", "position"]


class ClientStudentCreateSerializer(serializers.ModelSerializer):
    password = PasswordField()
    affiliated_client_company_name = serializers.ChoiceField(
        choices=[(name, name) for name in ClientCompany.names],
        error_messages={"invalid_choice": f"该客户公司不存在, 可选客户公司: {ClientCompany.names}"},
    )

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
