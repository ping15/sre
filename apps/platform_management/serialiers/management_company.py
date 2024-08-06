from rest_framework import serializers

from apps.platform_management.models import ManageCompany
from common.utils.drf.serializer_fields import ChoiceField


class ManagementCompanyListSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return {
            "id": obj.Type[obj.type.upper()].value,
            "name": obj.Type[obj.type.upper()].label,
        }

    class Meta:
        model = ManageCompany
        fields = "__all__"


class ManagementCompanyCreateSerializer(serializers.ModelSerializer):
    type = ChoiceField(
        choices=ManageCompany.Type.choices, default=ManageCompany.Type.PARTNER.value
    )

    class Meta:
        model = ManageCompany
        fields = "__all__"
