import datetime

from django.db import transaction
from django.db.models import QuerySet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from apps.my_lectures.models import (Advertisement, InstructorEnrolment,
                                     InstructorEvent)
from apps.platform_management.models import Event, Instructor
from apps.teaching_space.models import TrainingClass
from apps.teaching_space.serializers.training_class import (
    TrainingClassAddInstructorSerializer, TrainingClassAdvertisementSerializer,
    TrainingClassCreateSerializer, TrainingClassListSerializer,
    TrainingClassPublishAdvertisementSerializer,
    TrainingClassRetrieveSerializer, TrainingClassSelectInstructorSerializer)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.response import Response


class TrainingClassModelViewSet(ModelViewSet):
    # permission_classes = [ManageCompanyAdministratorPermission | SuperAdministratorPermission]
    permission_classes = [AllowAny]
    queryset = TrainingClass.objects.all()
    serializer_class = TrainingClassCreateSerializer
    ACTION_MAP = {
        "list": TrainingClassListSerializer,
        "create": TrainingClassCreateSerializer,
        "retrieve": TrainingClassRetrieveSerializer,
        "add_instructor": TrainingClassAddInstructorSerializer,
        "publish_advertisement": TrainingClassPublishAdvertisementSerializer,
        "advertisement": TrainingClassAdvertisementSerializer,
        "select_instructor": TrainingClassSelectInstructorSerializer,
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
                event_name=f"[{training_class.affiliated_manage_company_name}]邀请你为"
                           f"[{training_class.target_client_company_name}]上课",
                initiator=self.request.user.username,
                training_class=training_class,
            )

        except Instructor.DoesNotExist:
            return Response(result=False, err_msg="该讲师不存在")

        return Response()

    @action(detail=True, methods=["POST"])
    def reassign_instructor(self, request, *args, **kwargs):
        training_class: TrainingClass = self.get_object()

        # 无讲师代办事件不可取消
        if not hasattr(training_class, "instructor_event") or training_class.instructor_event is None:
            return Response(result=False, err_msg="无讲师代办事件，无需撤销")

        # 如果培训班已开课，则无法移除该讲师
        if training_class.start_date >= datetime.datetime.now().date():
            return Response(result=False, err_msg="该培训班已开课，不可移除")

        with transaction.atomic():
            # 把该培训班的该讲师的日程取消
            if training_class.instructor:
                Event.objects.filter(
                    event_type=Event.EventType.CLASS_SCHEDULE.value, instructor=training_class.instructor).delete()

            # 删除讲师代办事件，取消培训班的讲师
            training_class.instructor_event.delete()
            training_class.instructor = None
            training_class.save()

        return Response()

    @action(detail=True, methods=["POST"])
    def revoke_instructor(self, request, *args, **kwargs):
        training_class: TrainingClass = self.get_object()

        # 无讲师代办事件不可取消
        if not hasattr(training_class, "instructor_event") or training_class.instructor_event is None:
            return Response(result=False, err_msg="无讲师代办事件，无需撤销")

        # 讲师已确认不可撤销
        if training_class.instructor_event.status == InstructorEvent.Status.AGREED:
            return Response(result=False, err_msg="该代办事件讲师已确认")

        # 删除讲师代办事件，取消培训班的讲师
        with transaction.atomic():
            training_class.instructor_event.delete()
            training_class.instructor = None
            training_class.save()

        return Response()

    @action(detail=True, methods=["POST"])
    def publish_advertisement(self, request, *args, **kwargs):
        validated_data = self.validated_data
        training_class: TrainingClass = self.get_object()
        now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)

        # 如果报名截止时间大于等于当前时间，不可发布广告
        if validated_data["deadline_datetime"] <= now:
            return Response(result=False, err_msg="报名截止时间小于等于当前时间，不可发布广告")

        # 如果开课时间大于等于当前时间，不可发布广告
        if training_class.start_date <= now.date():
            return Response(result=False, err_msg="开课时间小于等于当前时间，不可发布广告")

        # 发布广告
        Advertisement.objects.create(
            training_class=training_class,
            deadline_datetime=validated_data["deadline_datetime"],
            location=validated_data["location"],
        )

        return Response()

    @action(detail=True, methods=["GET"])
    def advertisement(self, request, *args, **kwargs):
        # 寻找培训班的广告的报名状况
        training_class: TrainingClass = self.get_object()
        instructor_enrolments: QuerySet["InstructorEnrolment"] = (
            training_class.advertisement.instructor_enrolments.all()
        )

        # 序列化数据
        serializer = self.get_serializer(instructor_enrolments, many=True)

        # 返回序列化后的数据
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def select_instructor(self, request, *args, **kwargs):
        validated_data = self.validated_data

        # 寻找培训班的广告的报名状况
        training_class: TrainingClass = self.get_object()
        instructor_enrolments: QuerySet["InstructorEnrolment"] = (
            training_class.advertisement.instructor_enrolments.all()
        )

        # 检查所有的状态是否为pending
        if not all(enrolment.status == InstructorEnrolment.Status.PENDING for enrolment in instructor_enrolments):
            return Response(result=False, err_msg="存在非待聘用状态")

        # 检查 instructor_enrolment_id 是否在 instructor_enrolments 中
        try:
            selected_enrolment = instructor_enrolments.get(id=validated_data["instructor_enrolment_id"])
        except InstructorEnrolment.DoesNotExist:
            return Response(result=False, err_msg="不存在该报名记录")

        # 更新状态
        for enrolment in instructor_enrolments:
            if enrolment.id == selected_enrolment.id:
                enrolment.status = InstructorEnrolment.Status.ACCEPTED
            else:
                enrolment.status = InstructorEnrolment.Status.REJECTED
            enrolment.save()

        return Response()
