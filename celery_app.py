from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta

import pytz
from celery import Celery
from celery.schedules import crontab, schedule
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

app = Celery('training_center_prod', timezone=settings.TIME_ZONE)

app.config_from_object('django.conf:settings', namespace='CELERY')

# 使用 django-celery-beat 作为调度器
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

# 设置时区
setattr(app, "timezone", pytz.timezone("Asia/Shanghai"))

# 定义定时任务
app.conf.beat_schedule = {
    # 每天检查一次开课时间
    'start-training-class': {
        'task': 'apps.teaching_space.tasks.start_training_class',
        'schedule': crontab(minute="00", hour="00"),
        'args': ()
    },

    # 通知学员参加考试
    'notify_student_take_exam': {
        'task': 'apps.teaching_space.tasks.notify_student_take_exam',
        'schedule': crontab(minute="00", hour="18"),
        'args': ()
    },

    # 通知讲师确认培训班排期
    'notify_teacher_confirm_schedule': {
        'task': 'apps.teaching_space.tasks.notify_teacher_confirm_schedule',
        'schedule': crontab(minute="00", hour="18"),
        'args': ()
    },

    # 每1分钟检查一次考试
    'detect_exam_end_time': {
        'task': 'apps.teaching_space.tasks.detect_exam_end_time',
        'schedule': schedule(run_every=timedelta(minutes=1)),
        'args': ()
    },
}

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
