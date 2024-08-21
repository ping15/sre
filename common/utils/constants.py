from django.db import models


class AppModule(models.TextChoices):
    PLATFORM_MANAGEMENT = "platform_management", "平台管理"
    TEACHING_SPACE = "teaching_space", "授课空间"
    MY_LECTURES = "my_lectures", "我的讲课"
    AUTHENTICATION = "authentication", "认证"
