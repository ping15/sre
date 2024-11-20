from rest_framework import serializers

from exam_system.models import ExamStudent


class HistoricalGradesListSerializer(serializers.ModelSerializer):
    # exam_info = serializers.ReadOnlyField()

    class Meta:
        model = ExamStudent
        fields = ["start_time", "exam_info", "student_name", "is_commit"]
