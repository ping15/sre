from rest_framework import serializers

from apps.platform_management.models import Instructor, CourseTemplate
from common.utils.drf.serializer_fields import PasswordField
from common.utils.drf.serializer_validator import BasicSerializerValidator


class InstructorListSerializer(serializers.ModelSerializer):
    password = PasswordField()

    class Meta:
        model = Instructor
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "password",
            "hours_taught",
            "satisfaction_score",
            "is_partnered",
            "introduction",
        ]


class InstructorCreateSerializer(serializers.ModelSerializer, BasicSerializerValidator):
    password = PasswordField()
    teachable_courses = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[(name, name) for name in CourseTemplate.names],
            error_messages={
                "invalid_choice": f"存在部分课程不存在, 可选课程: {CourseTemplate.names}"
            },
        )
    )

    class Meta:
        model = Instructor
        fields = "__all__"


class InstructorCalendarSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()


class InstructorRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        exclude = ["id", "hours_taught", "is_partnered"]


class InstructorBatchImportSerializer(serializers.Serializer):
    file = serializers.FileField()


class InstructorReviewSerializer(serializers.ModelSerializer):
    pass
