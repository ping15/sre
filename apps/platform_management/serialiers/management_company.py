from rest_framework import serializers

from apps.platform_management.models import ManageCompany
from common.utils.drf.serializer_fields import UniqueCharField


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
    name = UniqueCharField(label="公司名称", max_length=32)

    class Meta:
        model = ManageCompany
        fields = ["name", "email"]


class ManagementCompanyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManageCompany
        exclude = ["type"]


class ManagementCompanyPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManageCompany
        fields = "__all__"


class ManagementCompanyRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManageCompany
        exclude = ["id"]
