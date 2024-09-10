import base64
import binascii
import uuid

from django.http import FileResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.platform_management.serialiers.attachment import (
    FileDeleteSerializer,
    FileDownloadSerializer,
    FileUploadSerializer,
)
from common.utils.cos import cos_client
from common.utils.drf.response import Response


class FileUploadDownloadView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get_validated_data(self, serializer_class):
        data = self.request.query_params if self.request.method == "GET" else self.request.data
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def get(self, request, *args, **kwargs):
        """下载文件"""
        validated_data = self.get_validated_data(FileDownloadSerializer)

        try:
            original_filename = base64.urlsafe_b64decode(validated_data["file_key"].split('_', 1)[1].encode()).decode()

        except KeyError:
            return Response(result=False, err_msg="无法解析出文件名")

        except binascii.Error:
            return Response(result=False, err_msg="无法解码文件名")

        response: dict = cos_client.download_file(validated_data["file_key"])
        if response.get("error"):
            return Response(result=False, err_msg=response["error"])

        return FileResponse(
            response["Body"],
            filename=original_filename,
        )

    def post(self, request, *args, **kwargs):
        """上传文件"""
        validated_data = self.get_validated_data(FileUploadSerializer)

        file_key = str(uuid.uuid4()) + '_' + base64.urlsafe_b64encode(validated_data["file"].name.encode()).decode()
        response: dict = cos_client.upload_file_by_fp(validated_data["file"], file_key)
        if response.get("error"):
            return Response(result=False, err_msg=response["error"])

        return Response({
            "file_key": file_key,
            "file_name": validated_data["file"].name,
            "url": f"/api/platform_management/attachment/?file_key={file_key}",
        })

    def delete(self, request, *args, **kwargs):
        """删除文件"""
        validated_data = self.get_validated_data(FileDeleteSerializer)

        response: dict = cos_client.delete_file(validated_data["file_key"])
        if response.get("error"):
            return Response(result=False, err_msg=response["error"])

        return Response()
