from rest_framework import serializers

from apps.platform_management.serialiers.course_template import CourseTemplateSerializer
from apps.teaching_space.models import TrainingClass


class TrainingClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassListSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    instructor_name = serializers.ReadOnlyField()

    class Meta:
        model = TrainingClass
        fields = ["name", "status", "student_count", "instructor_name"]


class TrainingClassRetrieveSerializer(serializers.ModelSerializer):
    course = CourseTemplateSerializer()

    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingClass
        exclude = ["instructor"]
