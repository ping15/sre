from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.platform_management.models import (
    CourseTemplate,
    Instructor,
    ManageCompany,
    ClientCompany,
)


class TrainingClass(models.Model):
    """培训班"""

    # course = models.ForeignKey(
    #     CourseTemplate,
    #     verbose_name=_("课程"),
    #     on_delete=models.CASCADE,
    # )
    course_name = models.CharField(_("课程"), max_length=64, unique=True)
    session_number = models.CharField(_("课程期数"), max_length=32)
    status = models.CharField(
        _("状态"),
        max_length=16,
        # choices=[
        #     ('preparing', _('筹备中')),
        #     ('in_progress', _('开课中')),
        #     ('completed', _('已结课')),
        # ],
        # default='planned'
    )
    class_mode = models.CharField(
        _("上课模式"),
        # choices=[
        #     ('online', _("线上课")),
        #     ('offline', _("线下课")),
        # ],
        max_length=16,
    )
    student_count = models.IntegerField(_("学员数量"), default=0)
    start_date = models.DateField(_("开课时间"))
    assessment_method = models.CharField(
        _("考核方式"),
        # choices=[
        #     (..., _("闭卷考试")),
        #     (..., _("闭卷机考")),
        #     ("practical", _("实操")),
        #     ("defense", _("答辩")),
        # ],
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
    )
    hours_per_lesson = models.IntegerField(_("课程课时"), default=6)

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
        return self.instructor.name

    @property
    def affiliated_manage_company(self) -> ManageCompany:
        return self.target_client_company.manage_company

    @property
    def affiliated_manage_company_name(self) -> str:
        return self.affiliated_manage_company.name

    def __str__(self):
        return f"{self.course} - {self.session_number}"
