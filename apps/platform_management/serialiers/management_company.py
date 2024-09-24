from rest_framework import serializers

from apps.platform_management.models import ManageCompany
from common.utils.drf.serializer_fields import ChoiceField


class ManagementCompanyListSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(label="公司类型")
    type_id = serializers.SerializerMethodField(label="公司类型id")

    def get_type(self, obj):
        return obj.Type[obj.type.upper()].label

    def get_type_id(self, obj):
        return obj.Type[obj.type.upper()].value

    class Meta:
        model = ManageCompany
        fields = "__all__"


class ManagementCompanyCreateSerializer(serializers.ModelSerializer):
    type = ChoiceField(label="公司类型", choices=ManageCompany.Type.choices, default=ManageCompany.Type.PARTNER.value)

    class Meta:
        model = ManageCompany
        fields = "__all__"


class ManagementCompanyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManageCompany
        exclude = ["type"]


class ManagementCompanyPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManageCompany
        fields = "__all__"
