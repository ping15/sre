from rest_framework import serializers

from apps.platform_management.models import Administrator


class AdministratorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "password",
            "manage_company",
            "role",
        ]


class AdministratorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = "__all__"
