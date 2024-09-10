from rest_framework import serializers

from apps.my_lectures.models import InstructorEnrolment
from apps.platform_management.models import CourseTemplate
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

    class Meta:
        model = TrainingClass
        fields = ["id", "name", "status", "student_count", "instructor_name"]


class TrainingClassRetrieveSerializer(serializers.ModelSerializer):
    instructor = InstructorListSerializer()
    course = CourseTemplateCreateSerializer()
    certification_body = serializers.JSONField()
    name = serializers.ReadOnlyField()
    end_date = serializers.ReadOnlyField()
    instructor_count = serializers.SerializerMethodField(method_name="statistic_instructor_count")

    def statistic_instructor_count(self, obj: TrainingClass):
        if obj.publish_type == TrainingClass.PublishType.PUBLISH_ADVERTISEMENT:
            return InstructorEnrolment.objects.filter(advertisement__training_class=obj).count()

        if obj.publish_type == TrainingClass.PublishType.DESIGNATE_INSTRUCTOR:
            return 1

        return 0

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


class TrainingClassDesignateInstructorSerializer(serializers.Serializer):
    instructor_id = serializers.IntegerField()
    deadline_date = serializers.DateField(required=False, allow_null=True)


# class TrainingClassRemoveInstructorSerializer(serializers.Serializer):
#     pass


class TrainingClassPublishAdvertisementSerializer(serializers.Serializer):
    location = serializers.CharField()
    deadline_datetime = serializers.DateTimeField()


class TrainingClassAdvertisementSerializer(serializers.ModelSerializer):
    instructor = InstructorListSerializer()
    # advertisement = AdvertisementListSerializer()

    class Meta:
        model = InstructorEnrolment
        fields = "__all__"


class TrainingClassSelectInstructorSerializer(serializers.Serializer):
    instructor_enrolment_id = serializers.IntegerField()
