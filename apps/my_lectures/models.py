from typing import List

from django.db import models

from apps.platform_management.models import Instructor
from apps.teaching_space.models import TrainingClass
from common.utils import global_constants


class InstructorEvent(models.Model):
    """讲师事项"""
    class Status(models.TextChoices):
        # 这里加减状态下面的方法也要调整
        PENDING = "pending", "待处理"
        AGREED = "agreed", "已同意"
        REJECTED = "rejected", "已拒绝"
        REMOVED = "removed", "已指定其他讲师"
        TIMEOUT = "timeout", "已超时"
        FINISHED = "finished", "已完成"
        REVOKE = "revoke", "已撤销"

        @classmethod
        def get_pending_statuses(cls) -> List:
            """[未办事项]状态列表"""
            return [cls.PENDING, cls.TIMEOUT]

        @classmethod
        def get_completed_statuses(cls) -> List:
            """[已办事项]状态列表"""
            return [cls.AGREED, cls.REJECTED, cls.REMOVED, cls.FINISHED, cls.REVOKE]

        @classmethod
        def get_handle_choices(cls):
            """用户可操作状态"""
            return [(cls.AGREED, "已同意"), (cls.REJECTED, "已拒绝")]

    class EventType(models.TextChoices):
        INVITE_TO_CLASS = "invite_to_class", "邀请上课"
        POST_CLASS_REVIEW = "post_class_review", "课后复盘"

    event_name = models.CharField("事项名", max_length=255)
    event_type = models.CharField("事件类型", max_length=32, choices=EventType.choices, default=EventType.INVITE_TO_CLASS)
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
    created_datetime = models.DateTimeField("发起时间", auto_now_add=True)
    start_date = models.DateField("开课时间", null=True, blank=True)
    review = models.TextField("课后复盘", default=global_constants.REVIEW_TEMPLATE)

    def __str__(self):
        return f"{self.instructor.username} -> {self.event_name}"

    class Meta:
        verbose_name = "讲师事项"
        verbose_name_plural = verbose_name


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
    is_revoked = models.BooleanField("是否已撤销", default=False)

    class Meta:
        verbose_name = "广告"
        verbose_name_plural = verbose_name


class InstructorEnrolment(models.Model):
    """报名状况"""

    class Status(models.TextChoices):
        ACCEPTED = "accepted", "已聘用"
        PENDING = "pending", "待聘用"
        NOT_ENROLLED = "not_enrolled", "未报名"
        REJECTED = "rejected", "未聘用"
        TIMEOUT = "timeout", "已过期"
        REVOKE = "revoke", "已撤销"

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
    status = models.CharField("状态", max_length=16, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return f"{self.instructor.username} -> {self.advertisement.training_class.name} -> {self.get_status_display()}"

    class Meta:
        verbose_name = "讲师报名表"
        verbose_name_plural = verbose_name
