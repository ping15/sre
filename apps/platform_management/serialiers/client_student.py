from rest_framework import serializers

from apps.platform_management.models import ClientStudent


class ClientStudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStudent
        exclude = ["department", "position"]


class ClientStudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStudent
        fields = "__all__"


class ClientStudentRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStudent
        fields = "__all__"
