from rest_framework import serializers
from apps.platform_management.models import CourseTemplate


class CourseTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTemplate
        fields = "__all__"


class CourseTemplateCreateSerializer(serializers.ModelSerializer):
    level = serializers.ChoiceField(choices=CourseTemplate.Level.choices)
    status = serializers.ChoiceField(choices=CourseTemplate.Status.choices)
    assessment_method = serializers.ChoiceField(
        choices=CourseTemplate.AssessmentMethod.choices
    )
    exam_type = serializers.ChoiceField(choices=CourseTemplate.ExamType.choices)
    exam_duration = serializers.ChoiceField(choices=CourseTemplate.ExamDuration.choices)
    exam_language = serializers.ChoiceField(choices=CourseTemplate.ExamLanguage.choices)
    certification_body = serializers.ChoiceField(
        choices=CourseTemplate.CertificationBody.choices
    )

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
