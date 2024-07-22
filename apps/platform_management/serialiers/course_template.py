from rest_framework import serializers
from apps.platform_management.models import CourseTemplate


class CourseTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTemplate
        fields = "__all__"


class CourseTemplateCreateSerializer(serializers.ModelSerializer):
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
