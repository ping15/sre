import datetime
from typing import List

import pytz
from django.db import transaction
from rest_framework import serializers

from apps.my_lectures.handles.event import EventHandler
from apps.my_lectures.models import InstructorEnrolment, InstructorEvent
from apps.platform_management.models import (
    Administrator,
    ClientCompany,
    ClientStudent,
    CourseTemplate,
    Event,
    ManageCompany,
)
from apps.platform_management.serialiers.client_company import (
    ClientCompanyListSerializer,
)
from apps.platform_management.serialiers.course_template import (
    CourseTemplateCreateSerializer,
)
from apps.platform_management.serialiers.instructor import InstructorListSerializer
from apps.teaching_space.models import TrainingClass
from common.utils import global_constants
from common.utils.drf.exceptions import TrainingClassScheduleConflictError
from common.utils.drf.serializer_fields import ChoiceField, ModelInstanceField
from common.utils.drf.serializer_validator import BasicSerializerValidator
from common.utils.sms import sms_client
from exam_system.models import ExamStudent


# region ModelViewSet
class TrainingClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingClass
        fields = ["id", "name", "status", "student_count", "instructor_name", "is_published"]


class TrainingClassRetrieveSerializer(serializers.ModelSerializer):
    instructor = InstructorListSerializer()
    course = CourseTemplateCreateSerializer()
    target_client_company = ClientCompanyListSerializer()
    name = serializers.ReadOnlyField()
    end_date = serializers.ReadOnlyField()
    student_count = serializers.ReadOnlyField()
    instructor_count = serializers.ReadOnlyField()

    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassCreateSerializer(serializers.ModelSerializer, BasicSerializerValidator):
    class_mode = ChoiceField(choices=TrainingClass.ClassMode.choices)
    assessment_method = ChoiceField(choices=CourseTemplate.AssessmentMethod.choices)

    def create(self, validated_data):
        user: Administrator = self.context["request"].user
        target_client_company: ClientCompany = validated_data["target_client_company"]

        # 客户公司名 + 课程名 + 期数 唯一
        self.assert_unique(target_client_company, validated_data["course"], validated_data["session_number"])

        # 非超级管理员不可创建其他管理公司下面客户公司的培训班
        affiliated_manage_company: ManageCompany = target_client_company.affiliated_manage_company
        if not user.is_super_administrator and user.affiliated_manage_company != affiliated_manage_company:
            raise serializers.ValidationError("非超级管理员不可创建其他管理公司下面客户公司的培训班")

        validated_data["creator"] = user.username
        # validated_data["client_students"] = target_client_company.students
        return super().create(validated_data)

    @staticmethod
    def assert_unique(target_client_company: ClientCompany, course: CourseTemplate, session_number: str):
        """客户公司名 + 课程名 + 期数 唯一"""

        if TrainingClass.objects.filter(
            target_client_company=target_client_company,
            course=course,
            session_number=session_number,
        ).exists():
            raise serializers.ValidationError(f"{target_client_company.name}-{course.name}-{session_number}已存在")

    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassUpdateSerializer(serializers.ModelSerializer):
    force_update = serializers.BooleanField(label="是否强制更新", default=False)

    def update(self, training_class: TrainingClass, validated_data):
        with transaction.atomic():
            # 1. 如果修改了开课时间，且此时培训班并没有排期，则直接修改
            # 2. 如果修改了开课时间，且此时培训班存在排期，且修改后的时间和讲师日程或不可用时间不冲突，
            #      则直接修改，且原有排期开课时间修改为新的开课时间
            # 3. 如果修改了开课时间，且此时培训班存在排期，且修改后的时间和讲师日程或不可用时间冲突，
            #      则不可修改，如果force_update为True强制更新，则情况原有的排期清除
            if "start_date" in validated_data and training_class.start_date != validated_data["start_date"]:
                force_update = validated_data.get("force_update", False)
                start_date = validated_data["start_date"]
                end_date = validated_data["start_date"] + datetime.timedelta(days=global_constants.CLASS_DAYS - 1)

                try:
                    schedule_event: Event = Event.objects.get(
                        event_type=Event.EventType.CLASS_SCHEDULE,
                        training_class=training_class
                    )

                    # 老的开课时间范围不需要检验是否有空
                    # 1. 当新的开课时间处于原来的课程期间时，开课时间为老的结课时间 + 1
                    # 2. 当新的结课时间处于原来的课程期间时，结课时间为老的开课时间 - 1
                    check_start_date, check_end_date = start_date, end_date
                    if training_class.start_date <= start_date <= training_class.end_date:
                        check_start_date = training_class.end_date + datetime.timedelta(days=1)
                    elif training_class.start_date <= end_date <= training_class.end_date:
                        check_end_date = training_class.start_date - datetime.timedelta(days=1)

                    # 修改后的时间讲师有空，修改排期的开课和结课时间
                    if EventHandler.is_instructor_idle(schedule_event.instructor, check_start_date, check_end_date):
                        # 通知讲师
                        errors: List[str] = sms_client.send_sms(
                            phone_numbers=[schedule_event.instructor.phone],
                            template_id="2330587",
                            template_params=[
                                training_class.name,
                                schedule_event.start_date.strftime("%Y-%m-%d"),
                                start_date.strftime("%Y-%m-%d"),
                            ],
                        )
                        if errors:
                            raise serializers.ValidationError(str(errors))

                        # 重新调整开课和结课时间
                        schedule_event.start_date = start_date
                        schedule_event.end_date = end_date
                        schedule_event.save()

                    # 如果排期冲突，且强制更新
                    elif force_update:
                        # 清空排期
                        schedule_event.delete()

                        # 通知讲师
                        if training_class.instructor:
                            errors: List[str] = sms_client.send_sms(
                                phone_numbers=[training_class.instructor.phone],
                                template_id="2330586",
                                template_params=[training_class.name]
                            )
                            if errors:
                                raise serializers.ValidationError(str(errors))

                        # 如果发布类型为[指定讲师]，将讲师的单据状态修改为[已指定其他讲师]
                        if training_class.publish_type == TrainingClass.PublishType.DESIGNATE_INSTRUCTOR:
                            InstructorEvent.objects. \
                                filter(training_class=training_class). \
                                update(status=InstructorEvent.Status.REMOVED)

                        # 如果发布类型为[发布广告]，将讲师报名单据的状态修改为[已撤销]
                        elif training_class.publish_type == TrainingClass.PublishType.PUBLISH_ADVERTISEMENT:
                            InstructorEnrolment.objects. \
                                filter(advertisement__training_class=training_class). \
                                update(status=InstructorEnrolment.Status.REVOKE)

                        # 培训班的发布类型修改为[未发布]
                        training_class.publish_type = TrainingClass.PublishType.NONE
                        training_class.instructor = None
                        training_class.save()

                    else:
                        raise TrainingClassScheduleConflictError("修改后的开课时间和原有讲师排期存在冲突")

                except Event.DoesNotExist:
                    # 培训班没有排期
                    pass

            # 如果课程，课程后缀出现变动，需要判断
            if any([
                training_class.course != validated_data.get("course", training_class.course),
                training_class.session_number != validated_data.get("session_number", training_class.session_number)
            ]):
                # 客户公司名 + 课程名 + 期数 唯一
                TrainingClassCreateSerializer.assert_unique(
                    target_client_company=validated_data["target_client_company"],
                    course=validated_data["course"],
                    session_number=validated_data["session_number"]
                )

            return super().update(training_class, validated_data)

    class Meta:
        model = TrainingClass
        exclude = ["review", "creator", "instructor"]
# endregion


# region 指定讲师
class TrainingClassDesignateInstructorSerializer(serializers.Serializer):
    """指定讲师"""
    instructor_id = serializers.IntegerField(label="讲师id")
    deadline_date = serializers.DateField(required=False, allow_null=True, label="讲师可预约时间")


class TrainingClassInstructorEventSerializer(serializers.ModelSerializer):
    """讲师事项"""
    status = serializers.CharField(label="讲师单据状态")
    instructor = InstructorListSerializer(label="讲师信息")

    class Meta:
        model = InstructorEvent
        fields = ["status", "instructor"]
# endregion


# region 发布广告
class TrainingClassPublishAdvertisementSerializer(serializers.Serializer):
    """发布广告"""
    location = serializers.CharField(label="上课地点")
    deadline_datetime = serializers.DateTimeField(label="开课截止时间")

    def validate(self, attrs):
        now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)

        # 如果报名截止时间小于等于当前时间，不可发布广告
        if attrs["deadline_datetime"] <= now:
            return serializers.ValidationError("报名截止时间小于等于当前时间，不可发布广告")

        return attrs


class TrainingClassAdvertisementSerializer(serializers.ModelSerializer):
    """讲师报名表"""
    instructor = InstructorListSerializer(label="讲师报名列表")

    class Meta:
        model = InstructorEnrolment
        fields = "__all__"


class TrainingClassSelectInstructorSerializer(serializers.Serializer):
    """挑选讲师"""
    instructor_enrolment_id = serializers.IntegerField(label="讲师报名单据id")
# endregion


# region 学员
class TrainingClassRemoveStudentSerializer(serializers.Serializer):
    """移除学员"""
    client_students = serializers.ListSerializer(child=ModelInstanceField(model=ClientStudent), label="客户学员列表")


class TrainingClassStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStudent
        exclude = ["last_login", "id_photo"]
# endregion


# region 满意度调查
class TrainingClassAnalyzeScoreSerializer(serializers.Serializer):
    """问卷星数据分析"""
    file = serializers.FileField(label="文件")
# endregion


# region 学员成绩
class TrainingCLassGradesSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(label="开考时间", format="%Y-%m-%d %H:%M:%S", default_timezone=pytz.utc)

    class Meta:
        model = ExamStudent
        fields = ["start_time", "exam_info", "student_name", "password"]


# endregion


# region 成绩
class TrainingClassModifyThresholdSerializer(serializers.Serializer):
    passing_score = serializers.IntegerField(label="分数线", min_value=0, max_value=100)
# endregion
