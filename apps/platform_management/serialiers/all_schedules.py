from rest_framework import serializers


class AllScheduleSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
