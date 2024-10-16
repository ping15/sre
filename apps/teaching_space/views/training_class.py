import datetime
import math
import os
from typing import List

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import FileResponse
from rest_framework.decorators import action

from apps.my_lectures.handles.event import EventHandler
from apps.my_lectures.models import Advertisement, InstructorEnrolment, InstructorEvent
from apps.platform_management.filters.client_student import ClientStudentFilterClass
from apps.platform_management.models import (
    Administrator,
    ClientStudent,
    CourseTemplate,
    Event,
    Instructor,
)
from apps.platform_management.serialiers.client_student import (
    ClientStudentCreateSerializer,
    ClientStudentListSerializer,
)
from apps.teaching_space.filters.training_class import TrainingClassFilterClass
from apps.teaching_space.models import TrainingClass
from apps.teaching_space.serializers.training_class import (
    TrainingClassAdvertisementSerializer,
    TrainingClassAnalyzeScoreSerializer,
    TrainingClassCreateSerializer,
    TrainingClassDesignateInstructorSerializer,
    TrainingClassInstructorEventSerializer,
    TrainingClassListSerializer,
    TrainingClassPublishAdvertisementSerializer,
    TrainingClassRemoveStudentSerializer,
    TrainingClassRetrieveSerializer,
    TrainingClassSelectInstructorSerializer,
    TrainingClassUpdateSerializer,
)
from common.utils import global_constants
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    ManageCompanyAdministratorPermission,
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response
from common.utils.excel_parser.mapping import TRAINING_CLASS_SCORE_EXCEL_MAPPING
from common.utils.excel_parser.parser import excel_to_list


class TrainingClassModelViewSet(ModelViewSet):
    permission_classes = [ManageCompanyAdministratorPermission | SuperAdministratorPermission]
    queryset = TrainingClass.objects.all()
    filter_class = TrainingClassFilterClass
    http_method_names = ["get", "post", "put", "patch"]
    ACTION_MAP = {
        "list": TrainingClassListSerializer,
        "create": TrainingClassCreateSerializer,
        "retrieve": TrainingClassRetrieveSerializer,
        "update": TrainingClassUpdateSerializer,
        "partial_update": TrainingClassUpdateSerializer,
        "designate_instructor": TrainingClassDesignateInstructorSerializer,
        "publish_advertisement": TrainingClassPublishAdvertisementSerializer,
        "advertisement": TrainingClassAdvertisementSerializer,
        "select_instructor": TrainingClassSelectInstructorSerializer,
        "instructor_event": TrainingClassInstructorEventSerializer,
        "analyze_score": TrainingClassAnalyzeScoreSerializer,
        "remove_student": TrainingClassRemoveStudentSerializer,
        "students": ClientStudentListSerializer,
        "add_students": ClientStudentCreateSerializer,
    }

    def get_queryset(self):
        user: Administrator = self.request.user
        queryset: QuerySet["TrainingClass"] = super().get_queryset()
        if not user.is_super_administrator:
            queryset = queryset.filter(
                target_client_company__affiliated_manage_company_name=user.affiliated_manage_company_name)

        return queryset

    @action(detail=True, methods=["GET"])
    def students(self, request, *args, **kwargs):
        """客户学员"""
        client_students = ClientStudentFilterClass(request.GET, queryset=self.get_object().client_students).qs
        return self.paginate_response(self.get_serializer(client_students, many=True).data)

    @action(detail=True, methods=["POST"])
    def add_students(self, request, *args, **kwargs):
        training_class: TrainingClass = self.get_object()
        with transaction.atomic():
            response = super().create(request, *args, **kwargs)

            # 将该学员添加到培训班中
            new_client_students = response.instance if isinstance(response.instance, list) else [response.instance]
            training_class.client_students.add(*new_client_students)
        return response

    @action(detail=True, methods=["POST"])
    def remove_student(self, request, *args, **kwargs):
        training_class: TrainingClass = self.get_object()
        client_students: QuerySet[ClientStudent] = self.validated_data["client_students"]
        training_class.client_students.remove(*client_students)
        return Response()

    @action(detail=True, methods=["GET"])
    def instructor_event(self, request, *args, **kwargs):
        """讲师事项"""
        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.DESIGNATE_INSTRUCTOR:
            return Response(result=False, err_msg="该培训班未处于[指定讲师]")

        if not hasattr(training_class, "instructor_event") or training_class.instructor_event is None:
            return Response(result=False, err_msg="该讲师无代办事项")

        instructor_event: InstructorEvent = training_class.instructor_event.last()

        # 如果该单据已经过了[截至时间]且处于[待处理]则超时了
        deadline_date: datetime.date = instructor_event.start_date or training_class.start_date
        if all([
            instructor_event.status != InstructorEvent.Status.TIMEOUT,
            instructor_event.status == InstructorEvent.Status.PENDING,
            deadline_date <= datetime.datetime.now().date()
        ]):
            instructor_event.status = InstructorEvent.Status.TIMEOUT
            instructor_event.save()

        return Response(self.get_serializer(instructor_event).data)

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
            start_date: datetime.date = validated_data.get("deadline_date", training_class.start_date)

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

            try:
                instructor: Instructor = Instructor.objects.get(id=validated_data["instructor_id"])
            except Instructor.DoesNotExist:
                return Response(result=False, err_msg="查不到该讲师")

            # 如果指定讲师的时候，开课时间和[不可用时间规则，取消单日不可用时间]规则冲突，不允许邀请
            if not EventHandler.is_range_date_usable(
                start_date=start_date,
                end_date=start_date + datetime.timedelta(days=global_constants.CLASS_DAYS - 1),
                instructor=instructor,
                without_training_class=True
            ):
                return Response(result=False, err_msg="该讲师已经在这个时间段存在不可用规则限制，不允许邀请")

            # 指定讲师
            training_class.instructor_id = validated_data["instructor_id"]

            # 修改培训班开课时间
            training_class.start_date = start_date

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
        training_class: TrainingClass = self.get_object()

        if not hasattr(training_class, "advertisement") or training_class.advertisement is None:
            return Response(result=False, err_msg="该培训班无广告")

        advertisement: Advertisement = training_class.advertisement
        instructor_enrolments: QuerySet["InstructorEnrolment"] = advertisement.instructor_enrolments.all().filter(
            status__in=[InstructorEnrolment.Status.PENDING, InstructorEnrolment.Status.ACCEPTED])
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
            "instructor_enrolments": self.paginate_response(self.get_serializer(
                instructor_enrolments, many=True).data).data["data"]
        })

    @action(detail=True, methods=["POST"])
    def select_instructor(self, request, *args, **kwargs):
        """从报名表中选择讲师"""
        validated_data = self.validated_data

        # 寻找培训班的广告的报名状况
        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.PUBLISH_ADVERTISEMENT:
            return Response(result=False, err_msg="该培训班未处于[发布广告]")

        instructor_enrolments: QuerySet[InstructorEnrolment] = training_class.advertisement.instructor_enrolments.all()

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
            # 更新状态，被选中的讲师状态为[ACCEPTED]，其他讲师为[REJECTED]
            for enrolment in instructor_enrolments:
                enrolment.status = (
                    InstructorEnrolment.Status.ACCEPTED
                    if enrolment.id == selected_enrolment
                    else InstructorEnrolment.Status.REJECTED
                )

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
            "education": self.transform_choices(ClientStudent.Education.choices),
        })

    @action(methods=["GET"], detail=False)
    def score_template(self, request, *args, **kwargs):
        return FileResponse(
            open(global_constants.TRAINING_CLASS_SCORE_TEMPLATE_PATH, "rb"),
            as_attachment=True,
            filename=os.path.basename(global_constants.TRAINING_CLASS_SCORE_TEMPLATE_PATH),
        )

    @action(methods=["POST"], detail=True)
    def analyze_score(self, request, *args, **kwargs):
        training_class: TrainingClass = self.get_object()

        # 如果培训班没有排期，直接返回
        if not InstructorEvent.objects.filter(training_class=training_class).exists():
            return Response(result=False, err_msg="该培训班没有排期")

        # 如果该培训班未处于[开课中]，直接返回
        if training_class.status != TrainingClass.Status.IN_PROGRESS:
            return Response(result=False, err_msg="该培训班未处于[开课中]")

        # 如果该培训班未到达结课时间，直接返回
        if datetime.datetime.now().date() < training_class.end_date:
            return Response(result=False, err_msg="该培训班未到达结课时间")

        datas, err_msg = excel_to_list(self.validated_data["file"], TRAINING_CLASS_SCORE_EXCEL_MAPPING)
        if err_msg:
            return Response(result=False, err_msg=err_msg)

        with transaction.atomic():
            # 统计讲师平均分
            scores: List[float] = [float(data_dict["score"]) for data_dict in datas]
            average_score: float = min(max(sum(scores) / len(scores), 0), 5)

            # 如果讲师未评过分，即0.0分，则直接赋值
            # 否则平均之前的分数
            instructor: Instructor = training_class.instructor
            if math.ceil(instructor.satisfaction_score) > 0:
                average_score = (instructor.satisfaction_score + average_score) / 2.0

            instructor.satisfaction_score = round(average_score, 1)
            instructor.save()

            # 培训班状态流转为已结课
            training_class.status = TrainingClass.Status.COMPLETED
            training_class.save()

            # 相应讲师产生 [填写复盘] 单据
            InstructorEvent.objects.create(
                event_name=f"[{training_class.target_client_company_name}] 的课后复盘等待填写",
                event_type=InstructorEvent.EventType.POST_CLASS_REVIEW,
                initiator=training_class.creator,
                training_class=training_class,
                instructor=training_class.instructor,
            )

        return Response()
