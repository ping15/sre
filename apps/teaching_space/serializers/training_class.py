from rest_framework import serializers

from apps.platform_management.models import CourseTemplate
from apps.platform_management.serialiers.course_template import \
    CourseTemplateCreateSerializer
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
