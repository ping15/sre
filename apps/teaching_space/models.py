import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.platform_management.models import (
    ClientCompany,
    CourseTemplate,
    Instructor,
    ManageCompany,
)
from common.utils import global_constants


class TrainingClass(models.Model):
    """培训班"""

    class Status(models.TextChoices):
        PREPARING = "preparing", "筹备中"
        IN_PROGRESS = "in_progress", "开课中"
        COMPLETED = "completed", "已结课"

    class ClassMode(models.TextChoices):
        ONLINE = "online", "线上课"
        OFFLINE = "offline", "线下课"

    class PublishType(models.TextChoices):
        NONE = "none", "未发布"
        PUBLISH_ADVERTISEMENT = "publish_advertisement", "发布广告"
        DESIGNATE_INSTRUCTOR = "designate_instructor", "指定讲师"

    course = models.ForeignKey(
        CourseTemplate,
        related_name="training_classes",
        verbose_name=_("课程"),
        on_delete=models.CASCADE,
        null=True,
    )
    session_number = models.CharField(_("课程期数"), max_length=32)
    status = models.CharField(_("状态"), max_length=16, choices=Status.choices, default=Status.PREPARING)
    course_status = models.CharField(
        _("状态"),
        choices=CourseTemplate.Status.choices,
        max_length=32,
        default=CourseTemplate.Status.PREPARATION,
    )
    class_mode = models.CharField(
        _("上课模式"),
        choices=ClassMode.choices,
        max_length=16,
        default=ClassMode.ONLINE
    )
    start_date = models.DateField(_("开课时间"))
    assessment_method = models.CharField(
        _("考核方式"),
        choices=CourseTemplate.AssessmentMethod.choices,
        max_length=16,
    )
    certification = models.CharField(_("认证证书"), max_length=32, default="")
    location = models.CharField(_("开课地点"), max_length=32)
    target_client_company = models.ForeignKey(
        ClientCompany,
        related_name="training_classes",
        verbose_name=_("客户公司"),
        on_delete=models.CASCADE,
        null=True,
    )
    instructor = models.ForeignKey(
        Instructor,
        related_name="training_classes",
        verbose_name=_("讲师"),
        on_delete=models.CASCADE,
        null=True,
    )
    hours_per_lesson = models.IntegerField(_("课程课时"), default=6)
    review = models.TextField(_("课后复盘"), default="")

    publish_type = models.CharField("发布方式", max_length=24, choices=PublishType.choices, default=PublishType.NONE)
    creator = models.CharField("创建人", max_length=32, default="")

    questionnaire_qr_code = models.JSONField(_("问卷二维码"), default=dict)

    @property
    def course_name(self) -> CourseTemplate:
        """课程名称"""
        return CourseTemplate.objects.get(name=self.course.name)

    @property
    def name(self) -> str:
        """培训班名称"""
        return f"{self.course.name}-{self.session_number}"

    @property
    def target_client_company_name(self) -> str:
        return self.target_client_company.name

    @property
    def num_lessons(self) -> int:
        """课时数量"""
        return self.course.num_lessons

    @property
    def instructor_name(self) -> str:
        """讲师名称"""
        return self.instructor.username if self.instructor else ""

    @property
    def affiliated_manage_company(self) -> ManageCompany:
        """管理公司"""
        return self.target_client_company.affiliated_manage_company

    @property
    def affiliated_manage_company_name(self) -> str:
        """管理公司名称"""
        return self.affiliated_manage_company.name

    @property
    def end_date(self) -> datetime.date:
        """结课时间"""
        return self.start_date + datetime.timedelta(days=global_constants.CLASS_DAYS - 1)

    @property
    def student_count(self) -> int:
        """学员数量"""
        return self.target_client_company.student_count

    @property
    def instructor_count(self) -> int:
        """讲师数量"""
        from apps.my_lectures.models import InstructorEnrolment

        if self.publish_type == TrainingClass.PublishType.PUBLISH_ADVERTISEMENT:
            return InstructorEnrolment.objects.filter(advertisement__training_class=self).count()

        if self.publish_type == TrainingClass.PublishType.DESIGNATE_INSTRUCTOR:
            return 1

        return 0

    def __str__(self):
        return self.name
