from rest_framework import serializers

from apps.platform_management.models import CourseTemplate
from common.utils.drf.serializer_fields import BlankableDateField, ChoiceField


class CourseTemplateCreateSerializer(serializers.ModelSerializer):
    level = ChoiceField(label="级别", choices=CourseTemplate.Level.choices)
    status = ChoiceField(label="课程状态", choices=CourseTemplate.Status.choices)
    assessment_method = ChoiceField(label="考核方式", choices=CourseTemplate.AssessmentMethod.choices)
    exam_type = serializers.ListSerializer(label="考试题型", child=ChoiceField(choices=CourseTemplate.ExamType.choices))
    exam_duration = ChoiceField(
        label="考试时长", choices=CourseTemplate.ExamDuration.choices, mapping={0: None, "": None}, allow_null=True)
    exam_language = ChoiceField(label="考试语言", choices=CourseTemplate.ExamLanguage.choices, mapping={"": None})
    certification_body = serializers.ListSerializer(
        label="认证机构", child=ChoiceField(choices=CourseTemplate.CertificationBody.choices))
    target_students = serializers.CharField(label="目标学员", default="", allow_null=True, allow_blank=True)
    learning_objectives = serializers.CharField(label="学习目标", default="", allow_null=True, allow_blank=True)
    learning_benefits = serializers.CharField(label="学习收益", default="", allow_null=True, allow_blank=True)
    version = serializers.CharField(label="版本", default="", allow_null=True, allow_blank=True)
    release_date = BlankableDateField(label="上线日期", required=False, allow_null=True)

    class Meta:
        model = CourseTemplate
        fields = "__all__"


class CourseTemplateListSerializer(serializers.ModelSerializer):
    course_module_count = serializers.ReadOnlyField(label="课程模块数量")

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
