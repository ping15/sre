from rest_framework import serializers

from apps.platform_management.models import ManageCompany


class ManagementCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ManageCompany
        fields = "__all__"
