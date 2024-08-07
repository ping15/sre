from rest_framework import serializers


class AllScheduleSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()