from rest_framework import serializers

from apps.platform_management.models import Instructor
from apps.platform_management.serialiers.client_student import ResourceInfoSerializer
from common.utils.drf.serializer_fields import ChoiceField, UniqueCharField
from common.utils.drf.serializer_validator import (
    BasicSerializerValidator,
    PhoneCreateSerializerValidator,
)
from common.utils.global_constants import AppModule


class InstructorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "hours_taught",
            "satisfaction_score",
            "is_partnered",
            "introduction",
            "city",
            "id_photo",
        ]


class InstructorCreateSerializer(serializers.ModelSerializer, PhoneCreateSerializerValidator, BasicSerializerValidator):
    phone = UniqueCharField(label="讲师手机号码", max_length=16)
    id_photo = ResourceInfoSerializer(label="资源信息", default={})

    class Meta:
        model = Instructor
        fields = "__all__"


class InstructorUpdateSerializer(serializers.ModelSerializer, BasicSerializerValidator):
    id_photo = ResourceInfoSerializer(label="资源信息", default={})

    def save(self, **kwargs):
        if not self.initial_data["phone"] == self.instance.phone:
            PhoneCreateSerializerValidator.validate_phone(self.initial_data["phone"])
        super().save(**kwargs)

    class Meta:
        model = Instructor
        fields = "__all__"


class InstructorPartialUpdateSerializer(serializers.ModelSerializer):
    id_photo = ResourceInfoSerializer(label="资源信息", default={})

    class Meta:
        model = Instructor
        fields = "__all__"


class InstructorCalendarSerializer(serializers.Serializer):
    start_date = serializers.DateField(label="开始时间")
    end_date = serializers.DateField(label="结束时间")


class InstructorRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        exclude = ["id", "hours_taught", "is_partnered", "last_login"]


class InstructorFilterConditionSerializer(serializers.Serializer):
    module = ChoiceField(label="模块", choices=AppModule.choices, default=AppModule.PLATFORM_MANAGEMENT)
