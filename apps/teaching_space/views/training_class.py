import datetime

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from rest_framework.decorators import action

from apps.my_lectures.handles.event import EventHandler
from apps.my_lectures.models import Advertisement, InstructorEnrolment, InstructorEvent
from apps.my_lectures.serializers.instructor_event import InstructorEventListSerializer
from apps.platform_management.models import CourseTemplate, Event
from apps.platform_management.serialiers.client_student import (
    ClientStudentListSerializer,
)
from apps.teaching_space.filters.training_class import TrainingClassFilterClass
from apps.teaching_space.models import TrainingClass
from apps.teaching_space.serializers.training_class import (
    TrainingClassAdvertisementSerializer,
    TrainingClassCreateSerializer,
    TrainingClassDesignateInstructorSerializer,
    TrainingClassListSerializer,
    TrainingClassPublishAdvertisementSerializer,
    TrainingClassRetrieveSerializer,
    TrainingClassSelectInstructorSerializer,
    TrainingClassUpdateSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    ManageCompanyAdministratorPermission,
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response


class TrainingClassModelViewSet(ModelViewSet):
    permission_classes = [ManageCompanyAdministratorPermission | SuperAdministratorPermission]
    # permission_classes = [AllowAny]
    queryset = TrainingClass.objects.all()
    serializer_class = TrainingClassCreateSerializer
    filter_class = TrainingClassFilterClass
    ACTION_MAP = {
        "list": TrainingClassListSerializer,
        "create": TrainingClassCreateSerializer,
        "retrieve": TrainingClassRetrieveSerializer,
        "update": TrainingClassUpdateSerializer,
        "designate_instructor": TrainingClassDesignateInstructorSerializer,
        "publish_advertisement": TrainingClassPublishAdvertisementSerializer,
        "advertisement": TrainingClassAdvertisementSerializer,
        "select_instructor": TrainingClassSelectInstructorSerializer,
    }

    @action(detail=True, methods=["GET"])
    def students(self, request, *args, **kwargs):
        """客户学员"""
        training_class: TrainingClass = self.get_object()
        return Response(ClientStudentListSerializer(training_class.target_client_company.students, many=True).data)

    @action(detail=True, methods=["GET"])
    def instructor_event(self, request, *args, **kwargs):
        """讲师事项"""
        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.DESIGNATE_INSTRUCTOR:
            return Response(result=False, err_msg="该培训班未处于[指定讲师]")

        if not hasattr(training_class, "instructor_event") or training_class.instructor_event is None:
            return Response(result=False, err_msg="该讲师无代办事项")

        instructor_event: InstructorEvent = training_class.instructor_event.last()

        # 如果该单据已经过了截至时间则超时了
        deadline_date: datetime.date = instructor_event.start_date or training_class.start_date
        if InstructorEvent.Status != InstructorEvent.Status.TIMEOUT and deadline_date <= datetime.datetime.now().date():
            instructor_event.status = InstructorEvent.Status.TIMEOUT
            instructor_event.save()

        return Response(InstructorEventListSerializer(instructor_event).data)

    @action(detail=True, methods=["POST"])
    def designate_instructor(self, request, *args, **kwargs):
        """指定讲师"""
        validated_data = self.validated_data
        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.NONE:
            return Response(result=False, err_msg="该培训班不处于未发布状态")

        # 如果培训班已开课，无法添加该讲师
        if training_class.start_date <= datetime.datetime.now().date():
            return Response(result=False, err_msg="该培训班开课时间小于等于当前时间，不可添加")

        # 如果已经有了讲师，不可添加
        if training_class.instructor:
            return Response(result=False, err_msg="该培训班已制定了讲师")

        try:
            start_date: datetime.date = validated_data.get("start_date", training_class.start_date)

            # 讲师无法同时在一天内给多个客户公司上课
            # 如果该讲师已经在这个时间段存在日程，不允许邀请
            # 假如讲师开课时间为a, a+1, 则如果说在a-1, a, a+1存在排期的话与讲师的排期冲突
            # 1. set(a, a+1) & set(a-1, a  ) = set(a)
            # 2. set(a, a+1) & set(a  , a+1) = set(a, a+1)
            # 3. set(a, a+1) & set(a+1, a+2) = set(a+1)
            if Event.objects.filter(
                event_type=Event.EventType.CLASS_SCHEDULE,
                instructor_id=validated_data["instructor_id"],
                start_date__range=(start_date - datetime.timedelta(days=1), start_date + datetime.timedelta(days=1)),
            ).exists():
                return Response(result=False, err_msg="该讲师已经在这个时间段存在日程，不允许邀请")

            # 如果指定讲师的时候，开课时间和[不可用时间规则，取消单日不可用时间]规则冲突，不允许邀请
            if not EventHandler.is_range_date_usable(
                start_date,
                start_date + datetime.timedelta(days=1),
                validated_data["instructor_id"],
                without_training_class=True
            ):
                return Response(result=False, err_msg="该讲师已经在这个时间段存在不可用规则限制，不允许邀请")

            # 指定讲师
            training_class.instructor_id = validated_data["instructor_id"]

            # 新增讲师事件
            InstructorEvent.objects.create(
                event_name=f"[{training_class.affiliated_manage_company_name}]邀请你为"
                           f"[{training_class.target_client_company_name}]上课",
                event_type=InstructorEvent.EventType.INVITE_TO_CLASS,
                initiator=training_class.creator,
                training_class=training_class,
                start_date=start_date,
                instructor_id=validated_data["instructor_id"],
            )

            # 培训班发布类型为[指定讲师]
            training_class.publish_type = TrainingClass.PublishType.DESIGNATE_INSTRUCTOR
            training_class.save()

        except IntegrityError:
            return Response(result=False, err_msg="该讲师不存在")

        return Response()

    @action(detail=True, methods=["POST"])
    def reassign_instructor(self, request, *args, **kwargs):
        """重新分配讲师"""
        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.DESIGNATE_INSTRUCTOR:
            return Response(result=False, err_msg="该培训班未处于[指定讲师]")

        # 无讲师代办事件不可取消
        if not hasattr(training_class, "instructor_event") or training_class.instructor_event is None:
            return Response(result=False, err_msg="无讲师代办事件，无需撤销")

        instructor_event: InstructorEvent = training_class.instructor_event.last()

        # 如果培训班已开课，则无法移除该讲师
        if training_class.start_date <= datetime.datetime.now().date():
            return Response(result=False, err_msg="该培训班已开课，不可移除")

        with transaction.atomic():
            # 当讲师同意时，会产生相应的日程，移除讲师时需将日程清除
            if training_class.instructor and instructor_event.status == InstructorEvent.Status.AGREED:
                # 把该培训班的该讲师的日程取消
                Event.objects.filter(
                    event_type=Event.EventType.CLASS_SCHEDULE.value, instructor=training_class.instructor).delete()

                # 讲师事项状态由[已同意]转成[已被移除]
                instructor_event.status = InstructorEvent.Status.REMOVED
                instructor_event.save()

            # 取消培训班的讲师
            training_class.instructor = None

            # 培训班发布类型为[未发布]
            training_class.publish_type = TrainingClass.PublishType.NONE
            training_class.save()

        return Response()

    @action(detail=True, methods=["POST"])
    def revoke_instructor(self, request, *args, **kwargs):
        """撤销讲师"""
        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.DESIGNATE_INSTRUCTOR:
            return Response(result=False, err_msg="该培训班未处于[指定讲师]")

        # 无讲师代办事件不可取消
        if not hasattr(training_class, "instructor_event") or training_class.instructor_event is None:
            return Response(result=False, err_msg="无讲师代办事件，无需撤销")

        instructor_event: InstructorEvent = training_class.instructor_event.last()

        # 讲师非待处理不可撤销
        if instructor_event.status != InstructorEvent.Status.PENDING:
            return Response(result=False, err_msg="讲师非待处理不可撤销")

        with transaction.atomic():
            # 删除讲师代办事件，取消培训班的讲师
            instructor_event.delete()
            training_class.instructor = None
            training_class.save()

            # 培训班发布类型为[未发布]
            training_class.publish_type = TrainingClass.PublishType.NONE
            training_class.save()

        return Response()

    @action(detail=True, methods=["POST"])
    def publish_advertisement(self, request, *args, **kwargs):
        """发布广告"""
        validated_data = self.validated_data
        training_class: TrainingClass = self.get_object()
        now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)

        # 如果培训班不处于未发布状态，不可发布
        if training_class.publish_type != TrainingClass.PublishType.NONE:
            return Response(result=False, err_msg="该培训班不处于未发布状态")

        # 如果报名截止时间大于等于当前时间，不可发布广告
        if validated_data["deadline_datetime"] <= now:
            return Response(result=False, err_msg="报名截止时间小于等于当前时间，不可发布广告")

        # 如果开课时间大于等于当前时间，不可发布广告
        if training_class.start_date <= now.date():
            return Response(result=False, err_msg="开课时间小于等于当前时间，不可发布广告")

        with transaction.atomic():
            # 清除原来的广告
            if hasattr(training_class, "advertisement") and training_class.advertisement is not None:
                training_class.advertisement.delete()

            # 发布广告
            Advertisement.objects.create(
                training_class=training_class,
                deadline_datetime=validated_data["deadline_datetime"],
                location=validated_data["location"],
            )

            # 培训班发布类型为[发布广告]
            training_class.publish_type = TrainingClass.PublishType.PUBLISH_ADVERTISEMENT
            training_class.instructor = None
            training_class.save()

        return Response()

    @action(detail=True, methods=["GET"])
    def advertisement(self, request, *args, **kwargs):
        """讲师报名表"""
        # 培训班，广告，报名状况
        training_class: TrainingClass = self.get_object()

        if not hasattr(training_class, "advertisement") or training_class.advertisement is None:
            return Response(result=False, err_msg="该培训班无广告")

        advertisement: Advertisement = training_class.advertisement
        instructor_enrolments: QuerySet["InstructorEnrolment"] = advertisement.instructor_enrolments.all()
        now: datetime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
        is_expired: bool = False

        # 如果未选择讲师且如果报名截止时间大于等于当前时间
        if (
            not instructor_enrolments.exclude(status=InstructorEnrolment.Status.PENDING).exists()
            and advertisement.deadline_datetime <= now
        ):
            # 培训班发布类型为[未发布]
            training_class.publish_type = TrainingClass.PublishType.NONE
            training_class.instructor = None
            training_class.save()

            # 讲师报名表清除
            training_class.advertisement.instructor_enrolments.all().delete()

            is_expired = True

        return Response({
            "is_expired": is_expired,
            "total": advertisement.enrolment_count,
            "deadline": advertisement.deadline_datetime,
            "instructor_enrolments": self.paginate_data(self.get_serializer(instructor_enrolments, many=True).data)
        })

    @action(detail=True, methods=["POST"])
    def select_instructor(self, request, *args, **kwargs):
        """从报名表中选择讲师"""
        validated_data = self.validated_data

        # 寻找培训班的广告的报名状况
        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.PUBLISH_ADVERTISEMENT:
            return Response(result=False, err_msg="该培训班未处于[发布广告]")

        instructor_enrolments: QuerySet["InstructorEnrolment"] = (
            training_class.advertisement.instructor_enrolments.all()
        )

        # 检查所有的状态是否为pending
        if not all(enrolment.status == InstructorEnrolment.Status.PENDING for enrolment in instructor_enrolments):
            return Response(result=False, err_msg="存在非待聘用状态")

        # 检查 instructor_enrolment_id 是否在 instructor_enrolments 中
        try:
            selected_enrolment: InstructorEnrolment = instructor_enrolments.get(
                id=validated_data["instructor_enrolment_id"])
        except InstructorEnrolment.DoesNotExist:
            return Response(result=False, err_msg="不存在该报名记录")

        with transaction.atomic():
            # 更新状态
            for enrolment in instructor_enrolments:
                if enrolment.id == selected_enrolment.id:
                    enrolment.status = InstructorEnrolment.Status.ACCEPTED
                else:
                    enrolment.status = InstructorEnrolment.Status.REJECTED
                enrolment.save()

            # 指定培训班的讲师
            training_class.instructor = selected_enrolment.instructor
            training_class.save()

            # 给选中的讲师安排日程
            EventHandler.create_event(training_class=training_class, event_type=Event.EventType.CLASS_SCHEDULE.value)

        return Response()

    @action(detail=False, methods=["GET"])
    def filter_condition(self, request, *args, **kwargs):
        return Response([
            {"id": "name", "name": "培训班名称", "children": []},
            {"id": "instructor_name", "name": "讲师", "children": []},
        ])

    @action(detail=False, methods=["GET"])
    def mapping(self, request, *args, **kwargs):
        return Response({
            "status": self.transform_choices(TrainingClass.Status.choices),
            "class_mode": self.transform_choices(TrainingClass.ClassMode.choices),
            "publish_type": self.transform_choices(TrainingClass.PublishType.choices),
            "assessment_method": self.transform_choices(CourseTemplate.AssessmentMethod.choices),
        })
