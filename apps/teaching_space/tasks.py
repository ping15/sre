from celery_app import app
from common.utils import colorize


@app.task(bind=True)
@colorize.task_decorator
def start_training_class(*args, **kwargs):
    print("start detect start_training_class")


@app.task(bind=True)
@colorize.task_decorator
def finish_training_class(*args, **kwargs):
    print("start detect finish_training_class")
