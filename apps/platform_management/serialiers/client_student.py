from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from apps.platform_management.models import ClientStudent
from common.utils.drf.serializer_fields import ChoiceField, MonthYearField
from common.utils.drf.serializer_validator import (
    BasicSerializerValidator,
    PhoneCreateSerializerValidator,
)
from common.utils.global_constants import AppModule


class ClientStudentListSerializer(serializers.ModelSerializer):
    education = ChoiceField(label="学历", choices=ClientStudent.Education.choices)

    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentCreateSerializer(
    serializers.ModelSerializer,
    PhoneCreateSerializerValidator,
    BasicSerializerValidator,
):
    education = ChoiceField(label="学历", choices=ClientStudent.Education.choices)

    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentUpdateSerializer(serializers.ModelSerializer, BasicSerializerValidator,):
    education = ChoiceField(label="学历", choices=ClientStudent.Education.choices)

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
        affiliated_client_company_name = serializers.CharField(label="客户公司名字", source="name")

    manage_company_name = serializers.CharField(label="管理公司名字", source="name")
    children = ClientCompanySerializer(label="客户公司列表", source="client_companies", many=True)


class ClientStudentBatchImportSerializer(
    serializers.ModelSerializer,
    PhoneCreateSerializerValidator,
    BasicSerializerValidator
):
    education = ChoiceField(label="学历", choices=ClientStudent.Education.choices)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["education"] = dict(ClientStudent.Education.choices).get(attrs["education"])
        return attrs

    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentStatisticSerializer(serializers.Serializer):
    start_date = MonthYearField()
    end_date = MonthYearField(time_delta=relativedelta(months=1, days=-1))


class ClientStudentFilterConditionSerializer(serializers.Serializer):
    module = ChoiceField(label="模块", choices=AppModule.choices, default=AppModule.PLATFORM_MANAGEMENT.value)
