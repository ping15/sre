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

# 培训班导入数据模板
TRAINING_CLASS_SCORE_TEMPLATE_PATH = "common/utils/excel_parser/templates/培训班数据导入模板.xlsx"

# 默认管理公司名称
DEFAULT_MANAGE_COMPANY = "鸿雪公司"

# 考试系统科目
subject_titles = ["理论知识", "实践技能"]
subject_percentage = {
    "理论知识": 0.7,
    "实践技能": 0.3,
}
assert sum(subject_percentage.values()) == 1
assert sorted(subject_titles) == sorted(list(subject_percentage.keys()))
