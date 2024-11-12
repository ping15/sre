import datetime

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


# region ModelViewSet
class TrainingClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingClass
        fields = ["id", "name", "status", "student_count", "instructor_name"]


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

        affiliated_manage_company: ManageCompany = target_client_company.affiliated_manage_company
        if not user.is_super_administrator and user.affiliated_manage_company != affiliated_manage_company:
            raise serializers.ValidationError("非超级管理员不可创建其他管理公司下面客户公司的培训班")

        validated_data["creator"] = user.username
        validated_data["client_students"] = target_client_company.students
        return super().create(validated_data)

    class Meta:
        model = TrainingClass
        fields = "__all__"


class TrainingClassUpdateSerializer(serializers.ModelSerializer):
    force_update = serializers.BooleanField(label="是否强制更新", default=False)

    def update(self, training_class: TrainingClass, validated_data):
        """
        # 1. 如果修改了开课时间，且此时培训班并没有排期，则直接修改
        # 2. 如果修改了开课时间，且此时培训班存在排期，且修改后的时间和讲师日程或不可用时间不冲突，
             则直接修改，且原有排期开课时间修改为新的开课时间
        # 3. 如果修改了开课时间，且此时培训班存在排期，且修改后的时间和讲师日程或不可用时间冲突，
             则不可修改，如果force_update为True强制更新，则情况原有的排期清除
        """
        if "start_date" in validated_data and training_class.start_date != validated_data["start_date"]:
            force_update = validated_data.get("force_update", False)
            start_date = validated_data["start_date"]
            end_date = validated_data["start_date"] + datetime.timedelta(days=global_constants.CLASS_DAYS - 1)

            try:
                schedule_event: Event = Event.objects.get(
                    event_type=Event.EventType.CLASS_SCHEDULE, training_class=training_class)

                # 修改后的时间讲师有空，修改排期的开课和结课时间
                if EventHandler.is_instructor_idle(schedule_event.instructor, start_date, end_date):
                    schedule_event.start_date = start_date
                    schedule_event.end_date = end_date
                    schedule_event.save()

                # 如果排期冲突，且强制更新
                elif force_update:
                    # 清空排期
                    schedule_event.delete()

                    # 如果发布类型为[指定讲师]，将讲师的单据状态修改为[已指定其他讲师]
                    if training_class.publish_type == TrainingClass.PublishType.DESIGNATE_INSTRUCTOR:
                        InstructorEvent.objects.filter(training_class=training_class).update(
                            status=InstructorEvent.Status.REMOVED)

                    # 如果发布类型为[发布广告]，将讲师报名单据的状态修改为[已撤销]
                    elif training_class.publish_type == TrainingClass.PublishType.PUBLISH_ADVERTISEMENT:
                        InstructorEnrolment.objects.filter(advertisement__training_class=training_class).update(
                            status=InstructorEnrolment.Status.REVOKE)

                    # 培训班的发布类型修改为[未发布]
                    training_class.publish_type = TrainingClass.PublishType.NONE
                    training_class.instructor = None
                    training_class.save()

                else:
                    raise TrainingClassScheduleConflictError("修改后的开课时间和原有讲师排期存在冲突")

            except Event.DoesNotExist:
                # 培训班没有排期
                pass

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
