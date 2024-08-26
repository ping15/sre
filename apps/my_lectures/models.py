from django.db import models

from apps.teaching_space.models import TrainingClass


class InstructorEvent(models.Model):
    """讲师事项"""
    class Status(models.TextChoices):
        PENDING = 'pending', "待处理"
        AGREED = 'agreed', "已同意"
        REJECTED = 'rejected', "已拒绝"

    event_name = models.CharField("事项名", max_length=255)
    initiator = models.CharField("发起人", max_length=255)
    status = models.CharField("状态", max_length=50, choices=Status.choices, default=Status.PENDING.value)
    training_class = models.OneToOneField(
        TrainingClass,
        on_delete=models.CASCADE,
        verbose_name="培训班",
        related_name="instructor_event"
    )
    created_datetime = models.DateField("发起时间", auto_now_add=True)
    review = models.TextField("课后复盘", default="")
