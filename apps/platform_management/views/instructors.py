from rest_framework.viewsets import ModelViewSet

from common.permissions import InstructorPermission


class InstructorsModelViewSet(ModelViewSet):
    permission_classes = [InstructorPermission]