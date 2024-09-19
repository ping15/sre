from rest_framework.views import APIView

from apps.platform_management.models import Instructor
from apps.platform_management.serialiers.instructor import (
    InstructorRetrieveSerializer,
    InstructorUpdateSerializer,
)
from common.utils.drf.permissions import InstructorPermission
from common.utils.drf.response import Response


class BaseInfoApiView(APIView):
    permission_classes = [InstructorPermission]

    def get(self, request, *args, **kwargs):
        user: Instructor = self.request.user

        return Response(InstructorRetrieveSerializer(user).data)

    def put(self, request, *args, **kwargs):
        user: Instructor = self.request.user

        serializer = InstructorUpdateSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
