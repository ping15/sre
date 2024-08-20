from rest_framework import serializers

from apps.platform_management.models import Event


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
