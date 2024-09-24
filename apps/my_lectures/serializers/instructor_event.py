from rest_framework import serializers

from apps.my_lectures.models import InstructorEvent
from apps.teaching_space.models import TrainingClass
from common.utils.drf.serializer_fields import ChoiceField


class InstructorEventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorEvent
        fields = ["id", "event_name", "event_type", "initiator", "status", "created_datetime"]


class InstructorEventRetrieveSerializer(serializers.ModelSerializer):
    class TrainingInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = TrainingClass
            fields = [
                "name", "start_date", "end_date", "location",
                "target_client_company_name", "affiliated_manage_company_name"
            ]

    training_class = TrainingInfoSerializer()

    class Meta:
        model = InstructorEvent
        fields = [
            "id", "event_name", "event_type", "initiator", "status",
            "created_datetime", "training_class", "review"
        ]


class InstructorEventUpdateStatusSerializer(serializers.Serializer):
    status = ChoiceField(label="讲师事项状态", choices=InstructorEvent.Status.choices)


class InstructorEventUpdateReviewSerializer(serializers.Serializer):
    review = serializers.CharField(label="课后复盘内容")
