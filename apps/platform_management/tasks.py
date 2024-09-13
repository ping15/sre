import logging

from celery_app import app
from common.utils import colorize

logger = logging.getLogger(__name__)


@app.task(bind=True)
@colorize.task_decorator
def print_hello(*args, **kwargs):
    logger.info("EXECUTE ------------> print_hello")
    print(type(args[0]))
    print(f"args: {args}, kwargs: {kwargs}")


@app.task(bind=True)
@colorize.task_decorator
def checking_training_class(*args, **kwargs):
    print("EXECUTE ------------> checking_training_class")
    print(f"args: {args}, kwargs: {kwargs}")


@app.task(bind=True)
@colorize.task_decorator
def test(*args, **kwargs):
    print("EXECUTE ------------> test")
    print(f"args: {args}, kwargs: {kwargs}")