from rest_framework import serializers

from apps.platform_management.models import Instructor
from common.utils.drf.serializer_validator import BasicSerializerValidator


class InstructorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "hours_taught",
            "satisfaction_score",
            "is_partnered",
            "introduction",
        ]


class InstructorCreateSerializer(serializers.ModelSerializer, BasicSerializerValidator):
    class Meta:
        model = Instructor
        fields = "__all__"


class InstructorCalendarSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()


class InstructorRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        exclude = ["id", "hours_taught", "is_partnered"]


class InstructorBatchImportSerializer(serializers.Serializer):
    file = serializers.FileField()


class InstructorReviewSerializer(serializers.ModelSerializer):
    pass
