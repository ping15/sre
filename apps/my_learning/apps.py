from django.apps import AppConfig


class MyLearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.my_learning'
    verbose_name = "我的学习"
