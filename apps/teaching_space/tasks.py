import datetime
import logging
from typing import List

from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone

from apps.my_lectures.models import InstructorEvent
from apps.teaching_space.models import TrainingClass
from celery_app import app
from common.utils import colorize
from common.utils.sms import sms_client
from exam_system.models import ExamArrange, ExamStudent

logger = logging.getLogger(__name__)


@app.task(bind=True)
@colorize.colorize_func
def start_training_class(func):
    """开课检测"""
    now_date: datetime.date = datetime.datetime.now().date()

    # 寻找 [状态在<发布广告>或<指定讲师>] + [有课程排期] + [筹备中] + [时间到达开课时间] 的培训班
    training_classes_to_update: QuerySet["TrainingClass"] = TrainingClass.objects.filter(
        # 筹备中
        status=TrainingClass.Status.PREPARING,
        # 时间到达开课时间
        start_date__lte=now_date,
        # 状态在<发布广告>或<指定讲师>
        publish_type__in=[
            TrainingClass.PublishType.DESIGNATE_INSTRUCTOR, TrainingClass.PublishType.PUBLISH_ADVERTISEMENT
        ],
        # 有课程排期
        event__isnull=False,
    )

    # 将状态流转为 [开课中]
    update_count: int = training_classes_to_update.count()
    if update_count > 0:
        training_classes_to_update.update(status=TrainingClass.Status.IN_PROGRESS)

    logger.info(f"共有{update_count}条培训班记录由 [筹备中] 转成 [已开课] ")


@app.task(bind=True)
@colorize.colorize_func
def finish_training_class(func):
    """结课检测"""


@app.task(bind=True)
@colorize.colorize_func
def detect_exam_end_time(func):
    """检查考试结束时间"""
    # 这里考试系统的开考时间有八小时的时间差
    now = timezone.now() + datetime.timedelta(hours=8)

    update_exam_students: List[ExamStudent] = []
    for exam_student in ExamStudent.objects.filter(is_commit=False):
        exam = exam_student.exam_arrange

        # 如果未提交的考卷且到考试结束时间的
        if exam and exam.end_time <= now:
            # 自动提交
            exam_student.is_commit = True

            # 如果考试有开考时间，优先使用开考时间，否则使用考试结束时间
            exam_student.start_time = exam_student.start_time or exam.end_time

            # 考生结束考试时间为考试结束时间
            exam_student.completion_time = exam.end_time

            # 自动创建答案记录实例
            if not exam_student.has_grades:
                exam_student.auto_generate_grades()

            update_exam_students.append(exam_student)

    ExamStudent.objects. \
        bulk_update(update_exam_students, fields=["is_commit", "start_time", "completion_time"], batch_size=500)

    logger.info(f"共有{len(update_exam_students)}个学生自动提交")


@app.task(bind=True)
@colorize.colorize_func
def notify_student_take_exam(func):
    """提前两天通知考生参加考试"""
    errors: List[str] = []

    # 这里考试系统的开考时间有八小时的时间差
    now: datetime.datetime = timezone.now() + datetime.timedelta(hours=8)
    for exam in ExamArrange.objects.filter(start_time__range=[now, now + datetime.timedelta(days=2)]):
        if settings.ENABLE_NOTIFY_SMS:
            errors += sms_client.send_sms(
                phone_numbers=[student.phone for student in ExamStudent.objects.filter(exam_id=exam.id)],
                template_id="2330581",
                template_params=[
                    exam.training_class.name,
                    exam.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "xxx网址"
                ]
            )
        else:
            logger.info(f"模拟给{[student.phone for student in ExamStudent.objects.filter(exam_id=exam.id)]}"
                        f"发送短信，参与课程: {exam.training_class.name}, "
                        f"考试时间: {exam.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    if errors:
        logger.info(f"发送短信出现异常: {errors}")


@app.task(bind=True)
@colorize.colorize_func
def notify_teacher_confirm_schedule(func):
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
        if settings.ENABLE_NOTIFY_SMS:
            errors += sms_client.send_sms(
                phone_numbers=[instructor_event.training_class.instructor.phone],
                template_id="2330584",
                template_params=[instructor_event.training_class.name],
            )
        else:
            logger.info(f"模拟给[{instructor_event.training_class.instructor.username}]发送短信，"
                        f"确认课程[{instructor_event.training_class.name}]")

    if errors:
        logger.info(f"发送短信出现异常: {errors}")
