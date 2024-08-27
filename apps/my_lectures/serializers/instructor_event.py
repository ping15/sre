from rest_framework import serializers

from apps.my_lectures.models import InstructorEvent
from common.utils.drf.serializer_fields import ChoiceField


class InstructorEventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorEvent
        fields = "__all__"


class InstructorEventUpdateSerializer(serializers.Serializer):
    status = ChoiceField(choices=InstructorEvent.Status.choices)
