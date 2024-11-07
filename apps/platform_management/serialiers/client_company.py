from rest_framework import serializers

from apps.platform_management.models import ClientCompany
from common.utils.drf.serializer_fields import ChoiceField, UniqueCharField
from common.utils.drf.serializer_validator import BasicSerializerValidator


class ClientCompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientCompany
        fields = [
            "id",
            "name",
            "contact_email",
            "contact_phone",
            "contact_person",
            "affiliated_manage_company_name",
            "student_count",
        ]


class ClientCompanyRetrieveSerializer(serializers.ModelSerializer):
    # payment_method = serializers.CharField(source='get_payment_method_display')

    class Meta:
        model = ClientCompany
        fields = "__all__"


class ClientCompanyUpdateSerializer(serializers.ModelSerializer, BasicSerializerValidator):
    payment_method = ChoiceField(choices=ClientCompany.PaymentMethod.choices)

    class Meta:
        model = ClientCompany
        fields = "__all__"


class ClientCompanyCreateSerializer(ClientCompanyUpdateSerializer):
    name = UniqueCharField(label="客户公司", max_length=32)

    class Meta:
        model = ClientCompany
        fields = "__all__"
