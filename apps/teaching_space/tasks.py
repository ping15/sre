import datetime
import logging
from typing import List

from django.db.models import QuerySet

from apps.teaching_space.models import TrainingClass
from celery_app import app
from common.utils import colorize
from exam_system.models import ExamStudent

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
        start_date__gte=now_date,
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
    now = datetime.datetime.now()

    update_exam_students: List[ExamStudent] = []
    for exam_student in ExamStudent.objects.filter(is_commit=False):
        exam = exam_student.exam_arrange

        # 如果未提交的考卷且到考试结束时间的
        # 1. 自动提交
        # 2. 如果考试有开考时间，优先使用开考时间，否则使用考试结束时间
        # 3. 考生结束考试时间为考试结束时间
        if exam and exam.end_time.replace(tzinfo=None) <= now:
            exam_student.is_commit = True
            exam_student.start_time = exam_student.start_time or exam.end_time
            exam_student.completion_time = exam.end_time
            update_exam_students.append(exam_student)

    ExamStudent.objects.bulk_update(
        update_exam_students, fields=["is_commit", "start_time", "completion_time"], batch_size=500)

    logger.info(f"共有{len(update_exam_students)}个学生自动提交")
