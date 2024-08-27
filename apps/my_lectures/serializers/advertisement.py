from rest_framework import serializers

from apps.my_lectures.models import Advertisement


class AdvertisementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = "__all__"


class AdvertisementAdvertisementRegistrationSerializer(serializers.Serializer):
    advertisement_id = serializers.IntegerField()
