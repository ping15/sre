from rest_framework import serializers

from apps.platform_management.models import Event


class AllScheduleListSerializer(serializers.Serializer):
    start_date = serializers.DateField(label="开始时间")
    end_date = serializers.DateField(label="结束时间")


class AllScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
