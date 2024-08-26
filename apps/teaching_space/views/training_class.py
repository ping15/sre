import datetime

from rest_framework.decorators import action

from apps.my_lectures.models import InstructorEvent
from apps.platform_management.models import Event, Instructor
from apps.teaching_space.models import TrainingClass
from apps.teaching_space.serializers.training_class import (
    TrainingClassCreateSerializer, TrainingClassListSerializer,
    TrainingClassRetrieveSerializer)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (ManageCompanyAdministratorPermission,
                                          SuperAdministratorPermission)
from common.utils.drf.response import Response


class TrainingClassModelViewSet(ModelViewSet):
    permission_classes = [ManageCompanyAdministratorPermission | SuperAdministratorPermission]
    queryset = TrainingClass.objects.all()
    serializer_class = TrainingClassCreateSerializer
    ACTION_MAP = {
        "list": TrainingClassListSerializer,
        "create": TrainingClassCreateSerializer,
        "retrieve": TrainingClassRetrieveSerializer,
    }

    @action(detail=True, methods=["POST"])
    def add_instructor(self, request, *args, **kwargs):
        validated_data = self.validated_data
        training_class: TrainingClass = self.get_object()

        # 如果培训班已开课，无法添加该讲师
        if training_class.start_date >= datetime.datetime.now().date():
            return Response(result=False, err_msg="该培训班已开课，不可添加")

        # 如果已经有了讲师，不可添加
        if training_class.instructor:
            return Response(result=False, err_msg="该培训班已制定了讲师")

        # 指定讲师
        try:
            training_class.instructor = Instructor.objects.get(id=validated_data["instructor"])
            training_class.save()

            # 新增讲师事件
            InstructorEvent.objects.create(
                event_name=f"[{training_class.target_client_company_name}]邀请你为"
                           f"[{training_class.affiliated_manage_company_name}]上课",
                initiator=self.request.user.username,
                training_class=training_class,
            )

        except Instructor.DoesNotExist:
            return Response(result=False, err_msg="该讲师不存在")

        return Response()

    @action(detail=True, methods=["POST"])
    def remote_instructor(self, request, *args, **kwargs):
        training_class: TrainingClass = self.get_object()

        # 如果培训班已开课，则无法移除该讲师
        if training_class.start_date >= datetime.datetime.now().date():
            return Response(result=False, err_msg="该培训班已开课，不可移除")

        # 把该培训班的该讲师的日程取消
        if training_class.instructor:
            Event.objects.filter(
                event_type=Event.EventType.CLASS_SCHEDULE.value, instructor=training_class.instructor).delete()

        # 取消培训班的讲师
        training_class.instructor = None
        training_class.save()

        return Response()

    # def create(self, request, *args, **kwargs):
    #     with transaction.atomic():
    #         response = super().create(request, *args, **kwargs)
    #         training_class: TrainingClass = response.instance
    #         EventHandler.create_event(
    #             training_class=training_class,
    #             event_type=Event.EventType.CLASS_SCHEDULE.value,
    #         )
    #     return response
