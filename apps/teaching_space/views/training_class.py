import datetime
import math
import os
from collections import defaultdict
from typing import List

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import FileResponse
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny

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
    ClientStudentUpdateSerializer,
)
from apps.teaching_space.filters.training_class import TrainingClassFilterClass
from apps.teaching_space.models import TrainingClass
from apps.teaching_space.serializers.training_class import (
    TrainingClassAdvertisementSerializer,
    TrainingClassAnalyzeScoreSerializer,
    TrainingClassCreateSerializer,
    TrainingClassDesignateInstructorSerializer,
    TrainingCLassGradesSerializer,
    TrainingClassInstructorEventSerializer,
    TrainingClassListSerializer,
    TrainingClassModifyThresholdSerializer,
    TrainingClassPublishAdvertisementSerializer,
    TrainingClassRemoveStudentSerializer,
    TrainingClassRetrieveSerializer,
    TrainingClassSelectInstructorSerializer,
    TrainingClassStudentsSerializer,
    TrainingClassUpdateSerializer,
)
from common.utils import global_constants
from common.utils.drf.exceptions import TrainingClassScheduleConflictError
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    ManageCompanyAdministratorPermission,
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response
from common.utils.excel_parser.mapping import TRAINING_CLASS_SCORE_EXCEL_MAPPING
from common.utils.excel_parser.parser import excel_to_list
from common.utils.sms import sms_client
from exam_system.models import ExamArrange, ExamGrade, ExamStudent


class TrainingClassModelViewSet(ModelViewSet):
    permission_classes = [ManageCompanyAdministratorPermission | SuperAdministratorPermission]
    queryset = TrainingClass.objects.all()
    filter_class = TrainingClassFilterClass
    http_method_names = ["get", "post", "put", "patch"]
    ACTION_MAP = {
        # region ModelViewSet
        "list": TrainingClassListSerializer,
        "create": TrainingClassCreateSerializer,
        "retrieve": TrainingClassRetrieveSerializer,
        "update": TrainingClassUpdateSerializer,
        "partial_update": TrainingClassUpdateSerializer,
        # endregion

        # region 指定讲师
        "designate_instructor": TrainingClassDesignateInstructorSerializer,
        "instructor_event": TrainingClassInstructorEventSerializer,
        # endregion

        # region 发布广告
        "publish_advertisement": TrainingClassPublishAdvertisementSerializer,
        "advertisement": TrainingClassAdvertisementSerializer,
        "select_instructor": TrainingClassSelectInstructorSerializer,
        # endregion

        # region 学员
        "remove_student": TrainingClassRemoveStudentSerializer,
        "students": TrainingClassStudentsSerializer,
        "add_students": ClientStudentCreateSerializer,
        # endregion

        # region 满意度调查
        "analyze_score": TrainingClassAnalyzeScoreSerializer,
        # endregion

        # region 成绩
        "modify_threshold": TrainingClassModifyThresholdSerializer,
        # endregion
    }

    def get_queryset(self):
        user: Administrator = self.request.user
        queryset: QuerySet["TrainingClass"] = super().get_queryset()
        if not user.is_super_administrator:
            queryset = queryset.filter(
                target_client_company__affiliated_manage_company_name=user.affiliated_manage_company_name)

        return queryset

    # region ModelViewSet
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)

        except TrainingClassScheduleConflictError as e:
            return Response(result=True, err_msg=e.detail, code=e.status_code)
    # endregion

    # region 学员
    @action(detail=True, methods=["GET"])
    def students(self, request, *args, **kwargs):
        """客户学员"""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        training_class: TrainingClass = get_object_or_404(
            TrainingClass, **{self.lookup_field: self.kwargs[lookup_url_kwarg]})

        # client_students = ClientStudentFilterClass(request.GET, queryset=training_class.client_students).qs

        client_students = ClientStudentFilterClass(
            request.GET, queryset=training_class.client_students.prefetch_related("training_classes")
        ).qs
        return self.paginate_response(self.get_serializer(client_students, many=True).data)

    @action(detail=True, methods=["POST"])
    def add_students(self, request, *args, **kwargs):
        """添加学员"""
        training_class: TrainingClass = self.get_object()
        with transaction.atomic():
            response = super().create_for_user(
                ClientStudent,
                request,
                update_serializer=ClientStudentUpdateSerializer,
                create_serializer=ClientStudentCreateSerializer,
                *args,
                **kwargs
            )

            # 将该学员添加到培训班中
            new_client_students = response.instance if isinstance(response.instance, list) else [response.instance]

            training_class.client_students.add(*new_client_students)
        return response

    @action(detail=True, methods=["POST"])
    def remove_student(self, request, *args, **kwargs):
        """移除学员"""
        training_class: TrainingClass = self.get_object()
        client_students: QuerySet[ClientStudent] = self.validated_data["client_students"]
        training_class.client_students.remove(*client_students)
        return Response()
    # endregion

    # region 指定讲师
    @action(detail=True, methods=["GET"])
    def instructor_event(self, request, *args, **kwargs):
        """讲师事项"""
        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.DESIGNATE_INSTRUCTOR:
            return Response(result=False, err_msg="该培训班未处于[指定讲师]")

        if not hasattr(training_class, "instructor_event") or training_class.instructor_event is None:
            return Response(result=False, err_msg="该讲师无代办事项")

        instructor_event: InstructorEvent = training_class.instructor_event. \
            filter(event_type=InstructorEvent.EventType.INVITE_TO_CLASS). \
            last()

        # 如果该单据为[邀请上课]，且已经过了[截至时间]且处于[待处理]则超时了
        deadline_date: datetime.date = instructor_event.start_date or training_class.start_date
        if all([
            instructor_event.event_type == InstructorEvent.EventType.INVITE_TO_CLASS,
            instructor_event.status != InstructorEvent.Status.TIMEOUT,
            instructor_event.status == InstructorEvent.Status.PENDING,
            deadline_date <= timezone.now().date()
        ]):
            with transaction.atomic():
                # 单据状态修改为[已超时]
                instructor_event.status = InstructorEvent.Status.TIMEOUT
                instructor_event.save()

                # 培训班发布状态为[未发布]
                training_class.publish_type = TrainingClass.PublishType.NONE
                training_class.save()

        return Response(self.get_serializer(instructor_event).data)

    @action(detail=True, methods=["POST"])
    def designate_instructor(self, request, *args, **kwargs):
        """指定讲师"""
        validated_data = self.validated_data

        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.NONE:
            return Response(result=False, err_msg="该培训班不处于未发布状态")

        # 如果培训班已开课，无法添加该讲师
        if training_class.start_date <= timezone.now().date():
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

            # 通知讲师
            errors: List[str] = sms_client.send_sms(
                phone_numbers=[Instructor.objects.get(id=validated_data["instructor_id"]).phone],
                template_id="2330584",
                template_params=[training_class.name]
            )
            if errors:
                return Response(result=False, err_msg=errors)

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
        if training_class.start_date <= timezone.now().date():
            return Response(result=False, err_msg="该培训班已开课，不可移除")

        with transaction.atomic():
            # 当讲师同意时，会产生相应的日程，移除讲师时需将日程清除，并通知讲师
            if training_class.instructor and instructor_event.status == InstructorEvent.Status.AGREED:
                # 通知讲师
                errors: List[str] = sms_client.send_sms(
                    phone_numbers=[training_class.instructor.phone],
                    template_id="2330585",
                    template_params=[training_class.name],
                )
                if errors:
                    return Response(result=False, err_msg=str(errors))

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
    # endregion

    # region 发布广告
    @action(detail=True, methods=["POST"])
    def publish_advertisement(self, request, *args, **kwargs):
        """发布广告"""
        validated_data = self.validated_data
        training_class: TrainingClass = self.get_object()
        now = timezone.now()

        # 如果培训班不处于未发布状态，不可发布
        if training_class.publish_type != TrainingClass.PublishType.NONE:
            return Response(result=False, err_msg="该培训班不处于未发布状态")

        # 如果报名截止时间小于等于当前时间，不可发布广告
        if validated_data["deadline_datetime"] <= now:
            return Response(result=False, err_msg="报名截止时间小于等于当前时间，不可发布广告")

        # 如果报名截止时间大于开课时间，不可发布广告
        if validated_data["deadline_datetime"].date() > training_class.start_date:
            return Response(result=False, err_msg="报名截止时间大于开课时间，不可发布广告")

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
        now: datetime = timezone.now()
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
        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.PUBLISH_ADVERTISEMENT:
            return Response(result=False, err_msg="该培训班未处于[发布广告]")

        instructor_enrolments: QuerySet[InstructorEnrolment] = training_class.advertisement.instructor_enrolments.all()

        # 检查所有的状态是否为[代聘用]
        if not all(enrolment.status == InstructorEnrolment.Status.PENDING for enrolment in instructor_enrolments):
            return Response(result=False, err_msg="存在非待聘用状态")

        # 检查是否有该讲师报名记录
        try:
            selected_enrolment: InstructorEnrolment = instructor_enrolments.get(
                id=validated_data["instructor_enrolment_id"]
            )
        except InstructorEnrolment.DoesNotExist:
            return Response(result=False, err_msg="不存在该报名记录")

        with transaction.atomic():
            # 更新状态，被选中的讲师状态为[已聘用]，其他讲师为[未聘用]
            for enrolment in instructor_enrolments:
                enrolment.status = (
                    InstructorEnrolment.Status.ACCEPTED
                    if enrolment == selected_enrolment
                    else InstructorEnrolment.Status.REJECTED
                )
                enrolment.save()

            # 指定培训班的讲师
            training_class.instructor = selected_enrolment.instructor
            training_class.save()

            # 通知讲师
            errors: List[str] = sms_client.send_sms(
                phone_numbers=[selected_enrolment.instructor.phone],
                template_id="2330583",
                template_params=[training_class.name]
            )
            if errors:
                return Response(result=False, err_msg=errors)

            # 给选中的讲师安排日程
            EventHandler.create_event(training_class=training_class, event_type=Event.EventType.CLASS_SCHEDULE.value)

        return Response()

    @action(detail=True, methods=["POST"])
    def revoke_advertisement(self, request, *args, **kwargs):
        """撤销广告"""
        training_class: TrainingClass = self.get_object()

        if training_class.publish_type != TrainingClass.PublishType.PUBLISH_ADVERTISEMENT:
            return Response(result=False, err_msg="该培训班未处于[发布广告]")

        if training_class.status != TrainingClass.Status.PREPARING:
            return Response(result=False, err_msg="该培训班状态未处于[筹备中]")

        with transaction.atomic():
            # 通知讲师
            instructor_enrolments = InstructorEnrolment.objects.filter(advertisement__training_class=training_class)
            errors: List[str] = sms_client.send_sms(
                phone_numbers=[enrolment.instructor.phone for enrolment in instructor_enrolments],
                template_id="2334658",
                template_params=[training_class.name],
            )
            if errors:
                return Response(result=False, err_msg=errors)

            # 删除讲师报名单据
            instructor_enrolments.delete()

            # 培训班发布类型为[未发布]
            training_class.publish_type = TrainingClass.PublishType.NONE
            training_class.instructor = None
            training_class.save()

            # 广告单据修改为[已撤销]状态
            advertisement: Advertisement = training_class.advertisement
            advertisement.is_revoked = True
            advertisement.save()

            # 排期清除
            Event.objects.filter(event_type=Event.EventType.CLASS_SCHEDULE, training_class=training_class).delete()

        return Response()

    # endregion

    # region 其他
    @action(detail=False, methods=["GET"])
    def filter_condition(self, request, *args, **kwargs):
        """筛选条件"""
        return Response([
            {"id": "name", "name": "培训班名称", "children": []},
            {"id": "instructor_name", "name": "讲师", "children": []},
        ])

    @action(detail=False, methods=["GET"])
    def mapping(self, request, *args, **kwargs):
        """培训班映射常量"""
        return Response({
            "status": self.transform_choices(TrainingClass.Status.choices),
            "class_mode": self.transform_choices(TrainingClass.ClassMode.choices),
            "publish_type": self.transform_choices(TrainingClass.PublishType.choices),
            "assessment_method": self.transform_choices(CourseTemplate.AssessmentMethod.choices),
            "education": self.transform_choices(ClientStudent.Education.choices),
        })

    @action(detail=True, methods=["POST"])
    def cancel_training_class(self, request, *args, **kwargs):
        """取消培训班"""
        training_class: TrainingClass = self.get_object()

        # 如果培训班状态为[已结课]，不可取消
        if training_class.status == TrainingClass.Status.COMPLETED:
            return Response(result=False, err_msg="该培训班的状态为[已结课]，不可取消")

        with transaction.atomic():
            # 如果指定了讲师
            if training_class.publish_type == TrainingClass.PublishType.DESIGNATE_INSTRUCTOR:
                # 讲师的单据状态修改为[已撤销]
                InstructorEvent.objects. \
                    filter(instructor=training_class.instructor, training_class=training_class). \
                    update(status=InstructorEvent.Status.REVOKE)

                # 如果存在排期
                if Event.objects.filter(instructor=training_class.instructor, training_class=training_class).exists():
                    # 通知讲师
                    errors: List[str] = sms_client.send_sms(
                        phone_numbers=[training_class.instructor.phone],
                        template_id="2334657",
                        template_params=[training_class.name],
                    )
                    if errors:
                        return Response(result=False, err_msg=errors)

            # 如果发布了广告
            elif training_class.publish_type == TrainingClass.PublishType.PUBLISH_ADVERTISEMENT:
                # 广告的状态修改为[已撤销]
                advertisement: Advertisement = training_class.advertisement
                advertisement.is_revoked = True
                advertisement.save()

                # 通知讲师
                instructor_enrolments = InstructorEnrolment.objects.filter(advertisement__training_class=training_class)
                errors: List[str] = sms_client.send_sms(
                    phone_numbers=[enrolment.instructor.phone for enrolment in instructor_enrolments],
                    template_id="2334657",
                    template_params=[training_class.name],
                )
                if errors:
                    return Response(result=False, err_msg=errors)

                # 清除讲师报名单据
                instructor_enrolments.delete()

            # 如果说培训班状态为[未开课]
            if training_class.status == TrainingClass.Status.PREPARING and training_class.instructor:
                # 取消排期
                Event.objects.filter(instructor=training_class.instructor, training_class=training_class).delete()

                # 培训班讲师为空
                training_class.instructor = None

                # 发布状态为[未发布]
                training_class.publish_type = TrainingClass.PublishType.NONE

            # 培训班状态修改为[已取消]
            training_class.status = TrainingClass.Status.CANCELLED
            training_class.save()

        return Response()
    # endregion

    # region 满意度调查
    @action(methods=["GET"], detail=False)
    def score_template(self, request, *args, **kwargs):
        """问卷星Excel数据模板"""
        return FileResponse(
            open(global_constants.TRAINING_CLASS_SCORE_TEMPLATE_PATH, "rb"),
            as_attachment=True,
            filename=os.path.basename(global_constants.TRAINING_CLASS_SCORE_TEMPLATE_PATH),
        )

    @action(methods=["POST"], detail=True)
    def analyze_score(self, request, *args, **kwargs):
        """问卷星数据分析"""
        training_class: TrainingClass = self.get_object()

        # 如果培训班没有排期，直接返回
        if not InstructorEvent.objects.filter(training_class=training_class).exists():
            return Response(result=False, err_msg="该培训班没有排期")

        # 如果该培训班未处于[开课中]，直接返回
        if training_class.status != TrainingClass.Status.IN_PROGRESS:
            return Response(result=False, err_msg="该培训班未处于[开课中]")

        # 如果该培训班未到达结课时间，直接返回
        if timezone.now().date() <= training_class.end_date:
            return Response(result=False, err_msg="该培训班未到达结课时间")

        datas, err_msg = excel_to_list(self.validated_data["file"], TRAINING_CLASS_SCORE_EXCEL_MAPPING)
        if err_msg:
            return Response(result=False, err_msg=err_msg)

        if len(datas) == 0:
            return Response(result=False, err_msg="Excel数据为空")

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
    # endregion

    # region 成绩
    @action(methods=["GET"], detail=True)
    def grades(self, request, *args, **kwargs):
        """查看学员成绩"""
        training_class: TrainingClass = self.get_object()

        try:
            # 查找所有该培训班所有已提交的学生成绩单
            exam_students: QuerySet[ExamStudent] = ExamStudent.objects.filter(
                exam_id__in=ExamArrange.objects.filter(
                    training_class_id=training_class.id,
                    subject__display_name__in=global_constants.subject_titles
                ).values_list("id", flat=True),

                is_commit=1,
            )
        except ExamArrange.DoesNotExist:
            return Response(result=False, err_msg="该培训班未安排考试")

        # 根据学生名聚合考试
        union_student_grades, exam_usernames = defaultdict(list), set()
        for grade in TrainingCLassGradesSerializer(exam_students, many=True).data:
            exam_usernames.add(grade["student_name"])
            union_student_grades[grade.pop("student_name")].append(grade)

        # 【考试系统用户名】 -> 【SRE系统用户名】
        exam_username_to_sre_username = {
            user.phone: user.username for user in ClientStudent.objects.filter(phone__in=exam_usernames)
        }

        # 计算分数, 判断是否通过考试
        grade_infos: List[dict] = []
        for exam_username, grades in union_student_grades.items():
            # 是否完成考试并全部批卷
            is_finished: bool = len(grades) == len(global_constants.subject_titles)

            # 计算总分, sum(各科分数 ✖ 百分比)
            score = sum(
                grade["exam_info"]["score"] * global_constants.subject_percentage[grade["exam_info"]["subject_name"]]
                for grade in grades
            )

            grade_infos.append({
                "student_name": exam_username_to_sre_username[exam_username],
                "grades": grades,
                "score": round(score, 1) if is_finished else None,
                "is_pass": score >= training_class.passing_score if is_finished else None,
            })

        return self.paginate_response(grade_infos)

    @action(methods=["POST"], detail=True)
    def publish_grades(self, request, *args, **kwargs):
        """开放考生查询"""
        training_class: TrainingClass = self.get_object()
        now = timezone.now()

        if training_class.is_published:
            return Response(result=False, err_msg="该培训班成绩已发布")

        if ExamArrange.objects.filter(
            training_class_id=training_class.id,
            subject__display_name__in=global_constants.subject_titles
        ).count() != len(global_constants.subject_titles):
            return Response(result=False, err_msg=f"{global_constants.subject_titles}需要安排")

        # 对于每一场考试, 下面任何一种情况出现, 则不可发布成绩
        for exam in ExamArrange.objects.filter(training_class_id=training_class.id):
            # 如果未到达考试结束时间, 不可发布成绩
            if exam.end_time > now + datetime.timedelta(hours=8):
                return Response(result=False, err_msg=f"考试[{exam.title}]未到达考试结束时间")

            # 存在已答题未评分的题目, 不可发布成绩
            if ExamGrade.objects.filter(exam_id=exam.id, is_check=False).exists():
                return Response(result=False, err_msg=f"考试[{exam.title}]存在考题未评分")

            # 存在成绩未公示, 不可发布成绩
            if not exam.notice:
                return Response(result=False, err_msg=f"考试[{exam.title}]未公示")

        # 该培训班所有考试
        exam_arranges = ExamArrange.objects.filter(training_class_id=training_class.id)
        with transaction.atomic():
            # 培训班状态为已发布
            training_class.is_published = True
            training_class.save()

            # 将考生中未提交的自动提交
            ExamStudent.objects.filter(exam_id__in=exam_arranges.values_list("id", flat=True)).update(is_commit=True)

        return Response()

    @action(methods=["POST"], detail=True)
    def modify_threshold(self, request, *args, **kwargs):
        """修改分数线"""
        validated_data = self.validated_data
        training_class: TrainingClass = self.get_object()

        if training_class.is_published:
            return Response(result=False, err_msg="该培训班成绩已发布,不可修改分数线")

        # 修改分数线
        training_class.passing_score = validated_data["passing_score"]
        training_class.save()

        return Response()
    # endregion

    # region 私有函数
    # endregion

    @action(methods=["GET"], detail=False, permission_classes=[AllowAny])
    def detect(self, request, *args, **kwargs):
        """通知讲师确认课程安排"""
        errors: List[str] = []

        # 这里考试系统的开考时间有八小时的时间差
        now: datetime.datetime = timezone.now() + datetime.timedelta(hours=8)
        for instructor_event in InstructorEvent.objects.filter(
                # 两天内
                start_date__range=[now, now + datetime.timedelta(days=2)],
                # 邀请讲课
                event_type=InstructorEvent.EventType.INVITE_TO_CLASS,
                # 未处理
                status=InstructorEvent.Status.PENDING,
        ):
            errors += sms_client.send_sms(
                phone_numbers=[instructor_event.training_class.instructor.phone],
                template_id="2330584",
                template_params=[instructor_event.training_class.name],
            )

        if errors:
            Response(result=False, err_msg=str(errors))
        return Response()

    @action(methods=["GET"], detail=False, permission_classes=[AllowAny])
    def detect2(self, request, *args, **kwargs):
        """提前两天通知考生参加考试"""
        errors: List[str] = []

        # 这里考试系统的开考时间有八小时的时间差
        now: datetime.datetime = timezone.now() + datetime.timedelta(hours=8)
        for exam in ExamArrange.objects.filter(start_time__range=[now, now + datetime.timedelta(days=2)]):
            errors += sms_client.send_sms(
                phone_numbers=[student.phone for student in ExamStudent.objects.filter(exam_id=exam.id)],
                template_id="2330581",
                template_params=[
                    exam.training_class.name,
                    exam.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "xxx网址"
                ]
            )

        if errors:
            return Response(result=False, err_msg=str(errors))

        return Response()
