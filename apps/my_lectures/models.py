from django.db import models

from apps.platform_management.models import Instructor
from apps.teaching_space.models import TrainingClass


class InstructorEvent(models.Model):
    """讲师事项"""
    class Status(models.TextChoices):
        PENDING = "pending", "待处理"
        AGREED = "agreed", "已同意"
        REJECTED = "rejected", "已拒绝"
        REMOVED = "removed", "已被移除"
        TIMEOUT = "timeout", "已超时"

    event_name = models.CharField("事项名", max_length=255)
    initiator = models.CharField("发起人", max_length=255)
    status = models.CharField("状态", max_length=50, choices=Status.choices, default=Status.PENDING)
    training_class = models.ForeignKey(
        TrainingClass,
        on_delete=models.CASCADE,
        verbose_name="培训班",
        related_name="instructor_event"
    )
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        verbose_name="讲师",
        related_name="instructor_event",
        null=True,
        blank=True,
    )
    created_datetime = models.DateField("发起时间", auto_now_add=True)
    start_date = models.DateField("开课时间", null=True, blank=True)
    review = models.TextField("课后复盘", default="")


class Advertisement(models.Model):
    """广告"""

    training_class = models.OneToOneField(
        TrainingClass,
        on_delete=models.CASCADE,
        verbose_name="培训班",
        related_name="advertisement"
    )
    enrolment_count = models.IntegerField("报名人数", default=0)
    deadline_datetime = models.DateTimeField("报名截至时间")
    location = models.CharField("开课地点", max_length=255)

    class Meta:
        verbose_name = "广告"
        verbose_name_plural = verbose_name


class InstructorEnrolment(models.Model):
    """报名状况"""

    class Status(models.TextChoices):
        ACCEPTED = "accepted", "已聘用"
        PENDING = "pending", "待聘用"
        REJECTED = "rejected", "未聘用"

    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        verbose_name="讲师",
        related_name="enrolments"
    )
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        verbose_name="广告",
        related_name="instructor_enrolments"
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
