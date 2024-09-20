from rest_framework import serializers

from apps.my_lectures.models import InstructorEnrolment, InstructorEvent
from apps.platform_management.models import CourseTemplate
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
    course_status = ChoiceField(choices=CourseTemplate.Status.choices)
    class_mode = ChoiceField(choices=TrainingClass.ClassMode.choices)
    assessment_method = ChoiceField(choices=CourseTemplate.AssessmentMethod.choices)

    def create(self, validated_data):
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
    class Meta:
        model = TrainingClass
        exclude = ["review", "creator", "instructor"]


class TrainingClassInstructorEventSerializer(serializers.ModelSerializer):
    status = serializers.CharField(label="讲师单据状态")
    instructor = InstructorListSerializer(label="讲师信息")

    class Meta:
        model = InstructorEvent
        fields = ["status", "instructor"]
