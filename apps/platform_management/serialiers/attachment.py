from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class FileDownloadSerializer(serializers.ModelSerializer):
    file_key = serializers.CharField()
