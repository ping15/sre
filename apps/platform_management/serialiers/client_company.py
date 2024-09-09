from rest_framework import serializers

from apps.platform_management.models import ClientCompany
from common.utils.drf.serializer_fields import ChoiceField
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
    payment_method = serializers.CharField(source='get_payment_method_display')

    class Meta:
        model = ClientCompany
        fields = "__all__"


class ClientCompanyCreateSerializer(
    serializers.ModelSerializer, BasicSerializerValidator
):
    payment_method = ChoiceField(
        choices=ClientCompany.PaymentMethod.choices, read_only=False
    )

    class Meta:
        model = ClientCompany
        fields = "__all__"
