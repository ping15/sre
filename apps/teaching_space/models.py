from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.platform_management.models import (ClientCompany, CourseTemplate,
                                             Instructor, ManageCompany)


class TrainingClass(models.Model):
    """培训班"""

    # course = models.ForeignKey(
    #     CourseTemplate,
    #     verbose_name=_("课程"),
    #     on_delete=models.CASCADE,
    # )
    class Status(models.TextChoices):
        PREPARING = "preparing", "筹备中"
        IN_PROGRESS = "in_progress", "开课中"
        COMPLETED = "completed", "已结课"

    class ClassMode(models.TextChoices):
        ONLINE = "online", "线上课"
        OFFLINE = "offline", "线下课"

    course_name = models.CharField(_("课程"), max_length=64)
    session_number = models.CharField(_("课程期数"), max_length=32)
    status = models.CharField(
        _("状态"),
        max_length=16,
        choices=Status.choices,
    )
    class_mode = models.CharField(
        _("上课模式"),
        choices=ClassMode.choices,
        max_length=16,
    )
    student_count = models.IntegerField(_("学员数量"), default=0)
    start_date = models.DateField(_("开课时间"))
    assessment_method = models.CharField(
        _("考核方式"),
        choices=CourseTemplate.AssessmentMethod.choices,
        max_length=16,
    )
    certification = models.CharField(_("认证证书"), max_length=32)
    location = models.CharField(_("开课地点"), max_length=32)
    target_client_company_name = models.CharField(_("客户公司"), max_length=64)
    instructor = models.ForeignKey(
        Instructor,
        related_name="training_classes",
        verbose_name=_("讲师"),
        on_delete=models.CASCADE,
        null=True,
    )
    hours_per_lesson = models.IntegerField(_("课程课时"), default=6)
    review = models.TextField(_("课后复盘"), default="")

    @property
    def course(self) -> CourseTemplate:
        return CourseTemplate.objects.get(name=self.course_name)

    @property
    def name(self) -> str:
        return f"{self.course.name}-{self.session_number}"

    @property
    def target_client_company(self) -> ClientCompany:
        return ClientCompany.objects.get(name=self.target_client_company_name)

    @property
    def num_lessons(self) -> int:
        return self.course.num_lessons

    @property
    def instructor_name(self) -> str:
        return self.instructor.username if self.instructor else ""

    @property
    def affiliated_manage_company(self) -> ManageCompany:
        return self.target_client_company.affiliated_manage_company

    @property
    def affiliated_manage_company_name(self) -> str:
        return self.affiliated_manage_company.name

    def __str__(self):
        return f"{self.course} - {self.session_number}"
