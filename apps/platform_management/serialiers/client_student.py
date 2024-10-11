from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from apps.platform_management.models import Administrator, ClientCompany, ClientStudent
from common.utils.drf.serializer_fields import (
    ChoiceField,
    MonthYearField,
    UniqueCharField,
)
from common.utils.drf.serializer_validator import (
    BasicSerializerValidator,
    PhoneCreateSerializerValidator,
)
from common.utils.global_constants import AppModule


class ClientStudentListSerializer(serializers.ModelSerializer):
    affiliated_client_company_id = serializers.ReadOnlyField(source="affiliated_client_company.id")

    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentCreateSerializer(
    serializers.ModelSerializer,
    PhoneCreateSerializerValidator,
    BasicSerializerValidator,
):
    phone = UniqueCharField(label="学员手机号码", max_length=16)
    education = ChoiceField(label="学历", choices=ClientStudent.Education.choices)

    def create(self, validated_data):
        user: Administrator = self.context["request"].user
        try:
            client_company: ClientCompany = ClientCompany.objects.get(
                name=validated_data["affiliated_client_company_name"])
        except ClientCompany.DoesNotExist:
            raise serializers.ValidationError("该客户公司不存在")

        if all([
            not user.is_super_administrator,
            user.affiliated_manage_company != client_company.affiliated_manage_company
        ]):
            raise serializers.ValidationError("非超级管理员不可创建其他管理公司下面客户公司的学员")

        return super().create(validated_data)

    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentUpdateSerializer(serializers.ModelSerializer, BasicSerializerValidator):
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
