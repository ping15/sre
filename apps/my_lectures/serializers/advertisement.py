from rest_framework import serializers

from apps.my_lectures.models import Advertisement


class AdvertisementListSerializer(serializers.ModelSerializer):
    """广告列表"""
    class Meta:
        model = Advertisement
        fields = "__all__"


class AdvertisementAdvertisementRegistrationSerializer(serializers.Serializer):
    """参加报名"""
    advertisement_id = serializers.IntegerField(label="广告id")


class AdvertisementAdvertisementCancelSerializer(AdvertisementAdvertisementRegistrationSerializer):
    """取消报名"""
