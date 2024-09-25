from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class FileDownloadSerializer(serializers.Serializer):
    file_key = serializers.CharField()
    need_download = serializers.BooleanField(default=False)


class FileDeleteSerializer(serializers.Serializer):
    file_key = serializers.CharField()
