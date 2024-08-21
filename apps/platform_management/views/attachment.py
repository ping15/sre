# views.py
from django.http import FileResponse, Http404
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser

from apps.platform_management.models import Attachment
from apps.platform_management.serialiers.attachment import AttachmentSerializer
from common.utils.drf.response import Response


class FileUploadView(generics.CreateAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            attachment_instance = serializer.save()
            return Response(
                {
                    "id": attachment_instance.id,
                    "file_name": attachment_instance.file.name.split("/")[-1],
                    "url": attachment_instance.file.url,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDownloadView(generics.RetrieveAPIView):
    queryset = Attachment.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            attachment = self.get_object()
            return FileResponse(
                attachment.file,
                as_attachment=True,
                filename=attachment.file.name.split("/")[-1],
            )
        except Attachment.DoesNotExist:
            raise Http404
