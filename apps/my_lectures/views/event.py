from apps.my_lectures.handles.event import EventHandler
from apps.platform_management.models import Event
from apps.my_lectures.serializers.event import EventCreateSerializer
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import InstructorPermission
from common.utils.drf.response import Response


class EventModelViewSet(ModelViewSet):
    permission_classes = [InstructorPermission]
    queryset = Event.objects.all()
    ACTION_MAP = {
        "create": EventCreateSerializer,
    }

    def create(self, request, *args, **kwargs):
        event: Event = EventHandler.create_event(
            **self.validated_data, instructor=self.request.user
        )
        return Response()
