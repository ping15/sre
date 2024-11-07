from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from apps.platform_management.models import (
    Administrator,
    ClientCompany,
    ClientStudent,
    ManageCompany,
)
from common.utils.drf.serializer_fields import (
    ChoiceField,
    ModelInstanceField,
    MonthYearField,
    ResourceURLField,
    UniqueCharField,
    get_model_instance_or_raise,
)
from common.utils.drf.serializer_validator import (
    BasicSerializerValidator,
    PhoneCreateSerializerValidator,
)
from common.utils.global_constants import AppModule


class ResourceInfoSerializer(serializers.Serializer):
    file_key = serializers.CharField(label="文件标识符")
    file_name = serializers.CharField(label="文件名")
    url = ResourceURLField(label="文件路径")


class ClientStudentListSerializer(serializers.ModelSerializer):
    class TrainingClassListSerializer(serializers.Serializer):
        name = serializers.CharField()

    affiliated_client_company_id = serializers.ReadOnlyField(source="affiliated_client_company.id")
    training_classes = serializers.ListSerializer(child=TrainingClassListSerializer(), label="已上课程")

    class Meta:
        model = ClientStudent
        exclude = ["last_login", "id_photo"]


class ClientStudentCreateSerializer(
    serializers.ModelSerializer,
    PhoneCreateSerializerValidator,
    BasicSerializerValidator,
):
    phone = UniqueCharField(label="学员手机号码", max_length=16)
    education = ChoiceField(label="学历", choices=ClientStudent.Education.choices)
    id_photo = ResourceInfoSerializer(label="资源信息", default={})

    def to_internal_value(self, data):
        return super().to_internal_value(data)

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        # 非超级管理员不可创建其他管理公司下面客户公司的学员
        user: Administrator = self.context["request"].user
        client_company: ClientCompany = get_model_instance_or_raise(
            model=ClientCompany,
            field="name",
            value=validated_data["affiliated_client_company_name"]
        )
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
    id_photo = ResourceInfoSerializer(label="资源信息", default={})

    def save(self, **kwargs):
        # 只有修改的手机号和原来的手机号不一致需要校验唯一
        if self.initial_data["phone"] != self.instance.phone:
            PhoneCreateSerializerValidator.validate_phone(self.initial_data["phone"])
        return super().save(**kwargs)

    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentRetrieveSerializer(serializers.ModelSerializer):
    class TrainingClassListSerializer(serializers.Serializer):
        name = serializers.CharField()

    training_classes = serializers.ListSerializer(child=TrainingClassListSerializer(), label="已上课程")

    class Meta:
        model = ClientStudent
        exclude = ["last_login"]


class ClientStudentBatchImportSerializer(
    serializers.ModelSerializer,
    BasicSerializerValidator
):
    education = ChoiceField(label="学历", choices=ClientStudent.Education.choices)
    phone = serializers.CharField(label="学员手机号码", max_length=16)

    def validate(self, attrs):
        # attrs["education"] = dict(ClientStudent.Education.choices).get(attrs["education"])
        return attrs

    class Meta:
        model = ClientStudent
        exclude = ["last_login", "id_photo"]


class ClientStudentStatisticSerializer(serializers.Serializer):
    start_date = MonthYearField(label="开始时间")
    end_date = MonthYearField(time_delta=relativedelta(months=1, days=-1), label="结束时间")
    affiliated_manage_company = ModelInstanceField(model=ManageCompany, label="管理公司id")

    # def validate(self, attrs):
    #     attrs["client_company"] = get_model_instance_or_raise(ClientCompany, "id", attrs["affiliated_client_company"])
    #     return attrs


class ClientStudentFilterConditionSerializer(serializers.Serializer):
    module = ChoiceField(label="模块", choices=AppModule.choices, default=AppModule.PLATFORM_MANAGEMENT.value)
