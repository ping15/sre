import datetime

from django.db.models import Q, QuerySet

from apps.teaching_space.models import TrainingClass
from celery_app import app
from common.utils import colorize


@app.task(bind=True)
@colorize.task_decorator
def start_training_class(func):
    now_date = datetime.datetime.now().date()

    # 寻找 [状态在<发布广告>或<指定讲师>] + [筹备中] + [时间到达开课时间] 的培训班
    training_classes_to_update: QuerySet["TrainingClass"] = TrainingClass.objects.filter(
        Q(status=TrainingClass.Status.PREPARING) & Q(start_date__lte=now_date)
    )

    # 将状态流转为 [开课中]
    update_count: int = training_classes_to_update.count()
    if update_count > 0:
        training_classes_to_update.update(status=TrainingClass.Status.IN_PROGRESS)

    return update_count


@app.task(bind=True)
@colorize.task_decorator
def finish_training_class(func):
    print("start detect finish_training_class")
