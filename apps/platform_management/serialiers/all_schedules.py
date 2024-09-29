from rest_framework import serializers


class AllScheduleListSerializer(serializers.Serializer):
    start_date = serializers.DateField(label="开始时间")
    end_date = serializers.DateField(label="结束时间")
