from rest_framework import serializers

from exam_system.models import ExamStudent


class HistoricalGradesListSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ExamStudent
        fields = ["start_time", "exam_info"]
