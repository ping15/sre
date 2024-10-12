import datetime
import logging

from django.db.models import QuerySet

from apps.teaching_space.models import TrainingClass
from celery_app import app
from common.utils import colorize

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
    # now_date: datetime.date = datetime.datetime.now().date()
    #
    # # 寻找 [开课中] + [时间到达结课时间(开课时间 + 2天)] 的培训班
    # training_classes_to_update: QuerySet["TrainingClass"] = TrainingClass.objects.filter(
    #     # 开课中
    #     status=TrainingClass.Status.IN_PROGRESS,
    #     # 时间到达结课时间(开课时间 + 2天)
    #     start_date__lte=now_date - datetime.timedelta(days=global_constants.CLASS_DAYS),
    # )
    #
    # update_count: int = training_classes_to_update.count()
    # if update_count > 0:
    #     with transaction.atomic():
    #         # 相应讲师产生 [填写复盘] 单据
    #         instructor_events: List[InstructorEvent] = [
    #             InstructorEvent(
    #                 event_name=f"[{training_class.target_client_company_name}] 的课后复盘等待填写",
    #                 event_type=InstructorEvent.EventType.POST_CLASS_REVIEW,
    #                 initiator=training_class.creator,
    #                 training_class=training_class,
    #                 instructor=training_class.instructor,
    #             )
    #             for training_class in training_classes_to_update
    #         ]
    #         InstructorEvent.objects.bulk_create(instructor_events)
    #
    #         # 将状态流转为 [已结课]
    #         training_classes_to_update.update(status=TrainingClass.Status.COMPLETED)
    #
    # logger.info(f"共有{update_count}条培训班记录由 [已开课] 转成 [已结课] ")
