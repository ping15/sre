import base64
import binascii
import uuid

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import FileResponse
from rest_framework import generics

from common.utils.cos import cos_client
from common.utils.drf.response import Response


class FileUploadDownloadView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        """下载文件"""
        query_params = self.request.query_params

        if "file_key" not in query_params:
            return Response(result=False, err_msg="未传入file_key")

        try:
            original_filename = base64.urlsafe_b64decode(query_params["file_key"].split('_', 1)[1].encode()).decode()

        except KeyError:
            return Response(result=False, err_msg="无法解析出文件名")

        except binascii.Error:
            return Response(result=False, err_msg="无法解码文件名")

        response: dict = cos_client.download_file(query_params["file_key"])
        if response.get("error"):
            return Response(result=False, err_msg=response["error"])

        return FileResponse(response["Body"], filename=original_filename)

    def post(self, request, *args, **kwargs):
        """上传文件"""
        data = self.request.data

        if "file" not in data:
            return Response(result=False, err_msg="未传入file")

        if not isinstance(data["file"], InMemoryUploadedFile):
            return Response(result=False, err_msg="传入的file无法识别为文件")

        file_key = str(uuid.uuid4()) + '_' + base64.urlsafe_b64encode(data["file"].name.encode()).decode()
        response: dict = cos_client.upload_file_by_fp(data["file"], file_key)
        if response.get("error"):
            return Response(result=False, err_msg=response["error"])

        return Response({"file_key": file_key})
