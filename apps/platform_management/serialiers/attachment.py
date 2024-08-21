from rest_framework import serializers

from apps.platform_management.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["file"]
