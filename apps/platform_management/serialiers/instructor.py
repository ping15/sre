from rest_framework import serializers

from apps.platform_management.models import CourseTemplate, Instructor
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

    def create(self, validated_data):
        course_name_to_id = {course["name"]: course["id"] for course in CourseTemplate.objects.values("name", "id")}
        validated_data["teachable_courses"] = [
            course_name_to_id[course_name]
            for course_name in validated_data.get("teachable_courses", [])
            if course_name in course_name_to_id
        ]

        return super().create(validated_data)

    class Meta:
        model = Instructor
        fields = "__all__"


class InstructorUpdateSerializer(serializers.ModelSerializer, BasicSerializerValidator):
    id_photo = ResourceInfoSerializer(label="资源信息", default={})

    def update(self, instance, validated_data):
        # 修改后的手机号和原来的相同，不需要校验手机号唯一性
        if not self.initial_data["phone"] == self.instance.phone:
            PhoneCreateSerializerValidator.validate_phone(self.initial_data["phone"])

        course_name_to_id = {course["name"]: course["id"] for course in CourseTemplate.objects.values("name", "id")}
        validated_data["teachable_courses"] = [
            course_name_to_id[course_name]
            for course_name in validated_data.get("teachable_courses", [])
            if course_name in course_name_to_id
        ]

        return super().update(instance, validated_data)

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
    def to_representation(self, instance):
        instructor_info: dict = super().to_representation(instance)

        course_id_to_name = {course["id"]: course["name"] for course in CourseTemplate.objects.values("name", "id")}
        instructor_info["teachable_courses"] = [
            course_id_to_name[course_id]
            for course_id in instructor_info["teachable_courses"]
            if course_id in course_id_to_name
        ]

        return instructor_info

    def validate(self, attrs):
        return super().validate(attrs)

    class Meta:
        model = Instructor
        exclude = ["id", "hours_taught", "is_partnered", "last_login"]


class InstructorFilterConditionSerializer(serializers.Serializer):
    module = ChoiceField(label="模块", choices=AppModule.choices, default=AppModule.PLATFORM_MANAGEMENT)
