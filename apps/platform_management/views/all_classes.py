from apps.teaching_space.models import TrainingClass
from apps.platform_management.serialiers.all_classes import AllClassesListSerializer
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission


class AllClassesModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    queryset = TrainingClass.objects.all()
    ACTION_MAP = {
        "list": AllClassesListSerializer,
    }
