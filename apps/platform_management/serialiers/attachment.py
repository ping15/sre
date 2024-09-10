from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class FileDownloadSerializer(serializers.Serializer):
    file_key = serializers.CharField()


class FileDeleteSerializer(serializers.Serializer):
    file_key = serializers.CharField()
