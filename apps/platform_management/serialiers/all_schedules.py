from rest_framework import serializers

from apps.platform_management.models import Event


class AllScheduleListSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class AllScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
