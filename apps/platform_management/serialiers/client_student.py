from rest_framework import serializers

from apps.platform_management.models import ClientStudent, ClientCompany
from common.utils.drf.serializer_fields import ChoiceField
from common.utils.drf.serializer_validator import (
    BasicSerializerValidator,
    PhoneCreateSerializerValidator,
)
from common.utils.tools import reverse_dict


class ClientStudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentCreateSerializer(
    serializers.ModelSerializer,
    PhoneCreateSerializerValidator,
    BasicSerializerValidator,
):
    education = ChoiceField(choices=ClientStudent.Education.choices)

    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentUpdateSerializer(
    serializers.ModelSerializer,
    BasicSerializerValidator,
):
    education = ChoiceField(choices=ClientStudent.Education.choices)

    def save(self, **kwargs):
        if not self.initial_data["phone"] == self.instance.phone:
            PhoneCreateSerializerValidator.validate_phone(self.initial_data["phone"])
        super().save(**kwargs)

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


class ClientStudentBatchImportSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        data["education"] = reverse_dict(dict(ClientStudent.Education.choices)).get(
            data["education"]
        )
        return data

    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentStatisticSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
