from rest_framework import serializers

from apps.my_lectures.serializers.instructor_event import \
    InstructorEventListSerializer
from apps.platform_management.models import CourseTemplate
from apps.platform_management.serialiers.course_template import \
    CourseTemplateCreateSerializer
from apps.platform_management.serialiers.instructor import \
    InstructorListSerializer
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

    class Meta:
        model = TrainingClass
        fields = ["id", "name", "status", "student_count", "instructor_name"]


class TrainingClassRetrieveSerializer(serializers.ModelSerializer):
    course = CourseTemplateCreateSerializer()
    certification_body = serializers.JSONField()
    instructor_event = InstructorEventListSerializer()

    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassCreateSerializer(serializers.ModelSerializer, BasicSerializerValidator):
    status = ChoiceField(choices=TrainingClass.Status.choices)
    class_mode = ChoiceField(choices=TrainingClass.ClassMode.choices)
    assessment_method = ChoiceField(choices=CourseTemplate.AssessmentMethod.choices)
    certification_body = serializers.ListSerializer(child=ChoiceField(choices=CourseTemplate.CertificationBody.choices))

    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassAddInstructorSerializer(serializers.Serializer):
    instructor = serializers.IntegerField()


# class TrainingClassRemoveInstructorSerializer(serializers.Serializer):
#     pass


class TrainingClassPublishAdvertisementSerializer(serializers.Serializer):
    location = serializers.CharField()
    deadline_datetime = serializers.DateTimeField()


class TrainingClassAdvertisementSerializer(serializers.Serializer):
    status = serializers.CharField()
    instructor = InstructorListSerializer()


class TrainingClassSelectInstructorSerializer(serializers.Serializer):
    instructor_enrolment_id = serializers.IntegerField()
