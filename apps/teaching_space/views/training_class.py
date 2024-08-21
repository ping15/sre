from apps.teaching_space.models import TrainingClass
from apps.teaching_space.serializers.training_class import (
    TrainingClassCreateSerializer, TrainingClassListSerializer,
    TrainingClassRetrieveSerializer)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (ManageCompanyAdministratorPermission,
                                          SuperAdministratorPermission)


class TrainingClassModelViewSet(ModelViewSet):
    permission_classes = [ManageCompanyAdministratorPermission | SuperAdministratorPermission]
    queryset = TrainingClass.objects.all()
    serializer_class = TrainingClassCreateSerializer
    ACTION_MAP = {
        "list": TrainingClassListSerializer,
        "create": TrainingClassCreateSerializer,
        "retrieve": TrainingClassRetrieveSerializer,
    }

    # def create(self, request, *args, **kwargs):
    #     with transaction.atomic():
    #         response = super().create(request, *args, **kwargs)
    #         training_class: TrainingClass = response.instance
    #         EventHandler.create_event(
    #             training_class=training_class,
    #             event_type=Event.EventType.CLASS_SCHEDULE.value,
    #         )
    #     return response
