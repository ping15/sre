from rest_framework import serializers

from apps.platform_management.models import CourseTemplate
from common.utils.drf.serializer_fields import (
    ChoiceField,
    MappingField,
    UniqueCharField,
)


class CourseTemplateUpdateSerializer(serializers.ModelSerializer):
    level = ChoiceField(label="级别", choices=CourseTemplate.Level.choices)
    status = ChoiceField(label="课程状态", choices=CourseTemplate.Status.choices)
    assessment_method = ChoiceField(label="考核方式", choices=CourseTemplate.AssessmentMethod.choices)
    exam_type = serializers.ListSerializer(label="考试题型", child=ChoiceField(choices=CourseTemplate.ExamType.choices))
    exam_duration = MappingField(
        field=ChoiceField(label="考试时长", choices=CourseTemplate.ExamDuration.choices),
        mapping={0: None, "": None},
        allow_null=True
    )
    exam_language = MappingField(
        field=ChoiceField(label="考试语言", choices=CourseTemplate.ExamLanguage.choices),
        mapping={"": None},
        allow_null=True
    )
    certification_body = serializers.ListSerializer(
        label="认证机构",
        child=ChoiceField(choices=CourseTemplate.CertificationBody.choices)
    )
    target_students = serializers.CharField(label="目标学员", default="", allow_null=True, allow_blank=True)
    learning_objectives = serializers.CharField(label="学习目标", default="", allow_null=True, allow_blank=True)
    learning_benefits = serializers.CharField(label="学习收益", default="", allow_null=True, allow_blank=True)
    version = serializers.CharField(label="版本", default="", allow_null=True, allow_blank=True)
    release_date = MappingField(
        field=serializers.DateField(label="上线日期"),
        mapping={"": None},
        required=False,
        allow_null=True
    )
    num_questions = MappingField(
        field=serializers.IntegerField(label="考题数量"),
        mapping={"": None},
        required=False,
        allow_null=True
    )
    passing_score = MappingField(
        field=serializers.IntegerField(label="过线分数"),
        mapping={"": None},
        required=False,
        allow_null=True
    )

    class Meta:
        model = CourseTemplate
        fields = "__all__"


class CourseTemplateCreateSerializer(CourseTemplateUpdateSerializer):
    name = UniqueCharField(label="课程", max_length=32)


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
