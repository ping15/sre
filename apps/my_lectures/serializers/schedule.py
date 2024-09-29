from rest_framework import serializers

from apps.platform_management.models import Event
from common.utils.drf.serializer_fields import BlankableDateField, ChoiceField


class EventCreateSerializer(serializers.ModelSerializer):
    end_date = BlankableDateField(label="结束时间", allow_null=True, required=False)
    event_type = ChoiceField(label="事件类型", choices=Event.EventType.create_choices)
    freq_type = ChoiceField(label="周期类型", choices=Event.FreqType.choices, allow_null=True, required=False)
    freq_interval = serializers.ListSerializer(label="周期频率", child=serializers.IntegerField(), default=[])

    def validate(self, attrs):
        # 如果为[一次性规则]，只需要开始时间和结束时间
        if attrs["event_type"] == Event.EventType.ONE_TIME_UNAVAILABILITY and "end_date" not in attrs:
            raise serializers.ValidationError("[一次性规则]必须传结束时间")

        # 如果为[周期性规则]，可不填结束时间，但是必须有[周期类型]
        elif attrs["event_type"] == Event.EventType.RECURRING_UNAVAILABILITY and "freq_type" not in attrs:
            raise serializers.ValidationError("[周期性规则]必须传周期类型")

        if "end_date" in attrs and attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError("结束时间必须大于或等于开始时间")

        return attrs

    class Meta:
        model = Event
        fields = "__all__"


class EventListSerializer(serializers.Serializer):
    start_date = serializers.DateField(label="开始时间")
    end_date = serializers.DateField(label="结束时间")


class EventUpdateSerializer(EventCreateSerializer):
    pass


class EventRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "freq_type", "start_date", "end_date", "freq_interval", "event_type"]
