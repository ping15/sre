from apps.platform_management.filters.all_classes import AllClassesFilterClass
from apps.platform_management.serialiers.all_classes import AllClassesListSerializer
from apps.teaching_space.models import TrainingClass
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission


class AllClassesModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    queryset = TrainingClass.objects.all()
    filter_class = AllClassesFilterClass
    ACTION_MAP = {
        "list": AllClassesListSerializer,
    }
