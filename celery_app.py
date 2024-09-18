from __future__ import absolute_import, unicode_literals

import os

import pytz
from celery import Celery
from celery.schedules import crontab
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
    # 'print-hello-every-10-seconds': {
    #     'task': 'apps.platform_management.tasks.print_hello',
    #     'schedule': 10.0,
    #     'args': ()
    # },
    'start-training-class': {
        'task': 'apps.teaching_space.tasks.start_training_class',
        'schedule': crontab(minute="59", hour="09"),
        'args': ()
    },
    'finish-training-class': {
        'task': 'apps.teaching_space.tasks.finish_training_class',
        'schedule': crontab(minute="59", hour="09"),
        'args': ()
    },
}

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
