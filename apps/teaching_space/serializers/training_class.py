from rest_framework import serializers

from apps.my_lectures.models import InstructorEnrolment, InstructorEvent
from apps.platform_management.models import (
    Administrator,
    CourseTemplate,
    Event,
    ManageCompany,
)
from apps.platform_management.serialiers.client_company import (
    ClientCompanyListSerializer,
)
from apps.platform_management.serialiers.course_template import (
    CourseTemplateCreateSerializer,
)
from apps.platform_management.serialiers.instructor import InstructorListSerializer
from apps.teaching_space.models import TrainingClass
from common.utils.drf.serializer_fields import ChoiceField
from common.utils.drf.serializer_validator import BasicSerializerValidator


class TrainingClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassListSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    instructor_name = serializers.ReadOnlyField()
    student_count = serializers.ReadOnlyField()

    class Meta:
        model = TrainingClass
        fields = ["id", "name", "status", "student_count", "instructor_name"]


class TrainingClassRetrieveSerializer(serializers.ModelSerializer):
    instructor = InstructorListSerializer()
    course = CourseTemplateCreateSerializer()
    target_client_company = ClientCompanyListSerializer()
    name = serializers.ReadOnlyField()
    end_date = serializers.ReadOnlyField()
    student_count = serializers.ReadOnlyField()
    instructor_count = serializers.ReadOnlyField()

    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassCreateSerializer(serializers.ModelSerializer, BasicSerializerValidator):
    class_mode = ChoiceField(choices=TrainingClass.ClassMode.choices)
    assessment_method = ChoiceField(choices=CourseTemplate.AssessmentMethod.choices)

    def create(self, validated_data):
        user: Administrator = self.context["request"].user
        affiliated_manage_company: ManageCompany = validated_data["target_client_company"].affiliated_manage_company

        if not user.is_super_administrator and user.affiliated_manage_company != affiliated_manage_company:
            raise serializers.ValidationError("非超级管理员不可创建其他管理公司下面客户公司的培训班")

        validated_data["creator"] = self.context["request"].user.username
        return super().create(validated_data)

    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassDesignateInstructorSerializer(serializers.Serializer):
    instructor_id = serializers.IntegerField()
    deadline_date = serializers.DateField(required=False, allow_null=True)


class TrainingClassPublishAdvertisementSerializer(serializers.Serializer):
    location = serializers.CharField()
    deadline_datetime = serializers.DateTimeField()


class TrainingClassAdvertisementSerializer(serializers.ModelSerializer):
    instructor = InstructorListSerializer()

    class Meta:
        model = InstructorEnrolment
        fields = "__all__"


class TrainingClassSelectInstructorSerializer(serializers.Serializer):
    instructor_enrolment_id = serializers.IntegerField()


class TrainingClassUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance: TrainingClass, validated_data):
        if "start_date" in validated_data and instance.start_date != validated_data["start_date"]:
            if Event.objects.filter(event_type=Event.EventType.CLASS_SCHEDULE, training_class=instance).exists():
                raise serializers.ValidationError("该培训班存在排期，开课时间不可修改")
        return super().update(instance, validated_data)

    class Meta:
        model = TrainingClass
        exclude = ["review", "creator", "instructor"]


class TrainingClassInstructorEventSerializer(serializers.ModelSerializer):
    status = serializers.CharField(label="讲师单据状态")
    instructor = InstructorListSerializer(label="讲师信息")

    class Meta:
        model = InstructorEvent
        fields = ["status", "instructor"]


class TrainingClassAnalyzeScoreSerializer(serializers.Serializer):
    file = serializers.FileField(label="文件")
