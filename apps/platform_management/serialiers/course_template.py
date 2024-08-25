from rest_framework import serializers

from apps.platform_management.models import CourseTemplate
from common.utils.drf.serializer_fields import ChoiceField

# class CourseTemplateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CourseTemplate
#         fields = "__all__"


class CourseTemplateCreateSerializer(serializers.ModelSerializer):
    level = ChoiceField(choices=CourseTemplate.Level.choices)
    status = ChoiceField(choices=CourseTemplate.Status.choices)
    assessment_method = ChoiceField(choices=CourseTemplate.AssessmentMethod.choices)
    exam_type = serializers.ListSerializer(child=ChoiceField(choices=CourseTemplate.ExamType.choices))
    exam_duration = ChoiceField(choices=CourseTemplate.ExamDuration.choices)
    exam_language = ChoiceField(choices=CourseTemplate.ExamLanguage.choices)
    certification_body = serializers.ListSerializer(child=ChoiceField(choices=CourseTemplate.CertificationBody.choices))
    target_students = serializers.CharField(default="", allow_null=True, allow_blank=True)
    learning_objectives = serializers.CharField(default="", allow_null=True, allow_blank=True)
    learning_benefits = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = CourseTemplate
        fields = "__all__"


class CourseTemplateListSerializer(serializers.ModelSerializer):
    course_module_count = serializers.ReadOnlyField()

    class Meta:
        model = CourseTemplate
        fields = [
            "id",
            "name",
            "level",
            "num_lessons",
            "course_overview",
            "status",
            "course_module_count",
        ]
