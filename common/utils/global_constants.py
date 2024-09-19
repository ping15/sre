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


# 管理员提示语
ROLE_TOOLTIPS = """平台管理员：有系统全局的权限
鸿雪公司管理员：有鸿雪公司对应授课空间的权限（可管理对应的客户授课）
合作伙伴管理员：有合作伙伴公司对应授课空间的权限（可管理对应的客户授课）"""

# 上课天数
CLASS_DAYS = 2

# 下载文件URL
DOWNLOAD_URL = "/api/platform_management/attachment/"

# 课后复盘初始模板
REVIEW_TEMPLATE = """<h2>进展好的方面</h2>

<h2>进展的不太顺利的方面</h2>

<h2>学员总体情况 （基础、接受度、与工作相关度等）</h2>

<h2>课堂氛围（提问和讨论等）</h2>

<h2>关于教材（是否识别到需要优化和勘误的地方）</h2>"""
