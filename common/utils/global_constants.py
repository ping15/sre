from django.db import models


class AppModule(models.TextChoices):
    PLATFORM_MANAGEMENT = "platform_management", "平台管理"
    TEACHING_SPACE = "teaching_space", "授课空间"
    MY_LECTURES = "my_lectures", "我的讲课"
    AUTHENTICATION = "authentication", "认证"


class Role(models.TextChoices):
    SUPER_ADMINISTRATOR = "SUPER_ADMINISTRATOR", "超级管理员"
    MANAGEMENT_ADMINISTRATOR = "management_administrator", "管理公司管理员"
    INSTRUCTOR = "instructor", "讲师"
    CLIENT_STUDENT = "client_student", "客户学员"


ROLE_TOOLTIPS = """平台管理员：有系统全局的权限
鸿雪公司管理员：有鸿雪公司对应授课空间的权限（可管理对应的客户授课）
合作伙伴管理员：有合作伙伴公司对应授课空间的权限（可管理对应的客户授课）"""
