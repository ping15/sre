# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import os

# from blueapps.conf.default_settings import *  # noqa
# from blueapps.conf.log import get_logging_config_dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 这里是默认的 INSTALLED_APPS，大部分情况下，不需要改动
# 如果你已经了解每个默认 APP 的作用，确实需要去掉某些 APP，请去掉下面的注释，然后修改
INSTALLED_APPS = (
    # "bkoauth",
    # 框架自定义命令
    # "blueapps.contrib.bk_commands",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # account app
    # "blueapps.account",
    "django_extensions",
    # "drf_file_upload",
    "django_filters",
    "drf_yasg",
    "rest_framework",
    "django_celery_beat",

    "apps.platform_management",
    "apps.teaching_space",
    "apps.authentication",
    "apps.my_lectures",
)

# 请在这里加入你的自定义 APP
INSTALLED_APPS += (  # noqa
    "home_application",
    "mako_application",
)

# 这里是默认的中间件，大部分情况下，不需要改动
# 如果你已经了解每个默认 MIDDLEWARE 的作用，确实需要去掉某些 MIDDLEWARE，或者改动先后顺序，请去掉下面的注释，然后修改
MIDDLEWARE = (
    # request instance provider
    # 'blueapps.middleware.request_provider.RequestProvider',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # 跨域检测中间件， 默认关闭
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    # 蓝鲸静态资源服务
    # "whitenoise.middleware.WhiteNoiseMiddleware",
    # Auth middleware
    # "blueapps.account.middlewares.RioLoginRequiredMiddleware",
    # "blueapps.account.middlewares.WeixinLoginRequiredMiddleware",
    # 'common.utils.login.middleware.LoginRequiredMiddleware',
    # exception middleware
    # "blueapps.core.exceptions.middleware.AppExceptionMiddleware",
    # django国际化中间件
    "django.middleware.locale.LocaleMiddleware",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (os.path.join(BASE_DIR, "templates"),),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 自定义中间件
MIDDLEWARE += ()  # noqa

# 默认数据库AUTO字段类型
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# 所有环境的日志级别可以在这里配置
# LOG_LEVEL = 'INFO'

# STATIC_VERSION_BEGIN
# 静态资源文件(js,css等）在APP上线更新后, 由于浏览器有缓存,
# 可能会造成没更新的情况. 所以在引用静态资源的地方，都把这个加上
# Django 模板中：<script src="/a.js?v={{ STATIC_VERSION }}"></script>
# mako 模板中：<script src="/a.js?v=${ STATIC_VERSION }"></script>
# 如果静态资源修改了以后，上线前改这个版本号即可
# STATIC_VERSION_END
STATIC_VERSION = "1.0"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # noqa

# CELERY 开关，使用时请改为 True，修改项目目录下的 Procfile 文件，添加以下两行命令：
# worker: python manage.py celery worker -l info
# beat: python manage.py celery beat -l info
# 不使用时，请修改为 False，并删除项目目录下的 Procfile 文件中 celery 配置
IS_USE_CELERY = False

# 前后端分离开发配置开关，设置为True时dev和stag环境会自动加载允许跨域的相关选项
FRONTEND_BACKEND_SEPARATION = False

# CELERY 并发数，默认为 2，可以通过环境变量或者 Procfile 设置
CELERYD_CONCURRENCY = os.getenv("BK_CELERYD_CONCURRENCY", 2)  # noqa

# CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
CELERY_IMPORTS = ()

# log level setting
LOG_LEVEL = "INFO"

# load logging settings
# LOGGING = get_logging_config_dict(locals())
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#         },
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'debug.log'),
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console', 'file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'celery': {
#             'handlers': ['console', 'file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'apps.platform_management': {
#             'handlers': ['console', 'file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }

# 初始化管理员列表，列表中的人员将拥有预发布环境和正式环境的管理员权限
# 注意：请在首次提测和上线前修改，之后的修改将不会生效
INIT_SUPERUSER = []

AUTHENTICATION_BACKENDS = ["common.utils.auth.backends.ModelBackend"]

# 使用mako模板时，默认打开的过滤器：h(过滤html)
MAKO_DEFAULT_FILTERS = ["h"]

# BKUI是否使用了history模式
IS_BKUI_HISTORY_MODE = False

# 是否需要对AJAX弹窗登录强行打开
IS_AJAX_PLAIN_MODE = False

# 国际化配置
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)  # noqa

USE_TZ = True
TIME_ZONE = "Asia/Shanghai"
LANGUAGE_CODE = "zh-hans"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

LANGUAGES = (
    ("en", "English"),
    ("zh-hans", "简体中文"),
)

SECRET_KEY = "django-insecure-35imlrk$%wnuqejyqayeh1#=))b+9ovtqoqu*zhtr0@4=)4&t7"

ROOT_URLCONF = "urls"

# AUTH_USER_MODEL = "platform_management.Manager"
AUTH_USER_MODEL = 'platform_management.Administrator'

SITE_ID = 1

# COS配置
COS_SECRET_ID = os.environ.get("COS_SECRET_ID", "")
COS_SECRET_KEY = os.environ.get("COS_SECRET_KEY", "")
COS_REGION = os.environ.get("COS_REGION", "")
COS_BUCKET = os.environ.get("COS_BUCKET", "")

# Celery配置
CELERY_BROKER_URL = (f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:"
                     f"{os.environ.get('REDIS_PORT', '6379')}/{os.environ.get('REDIS_DB_INDEX', '0')}")
CELERY_RESULT_BACKEND = (f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:"
                         f"{os.environ.get('REDIS_PORT', '6379')}/{os.environ.get('REDIS_DB_INDEX', '0')}")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
DJANGO_CELERY_BEAT_TZ_AWARE = False

# django_filters默认lookup_expr
FILTERS_DEFAULT_LOOKUP_EXPR = "icontains"

# 是否启用SMS
ENABLE_SMS = bool(os.environ.get("ENABLE_SMS", False))
ENABLE_NOTIFY_SMS = bool(os.environ.get("ENABLE_NOTIFY_SMS", False))
SMS_USERNAME = os.environ.get("SMS_USERNAME", "")
SMS_PASSWORD = os.environ.get("SMS_PASSWORD", "")

# 默认ADMIN手机号码
ADMIN_PHONE = os.environ.get("ADMIN_PHONE", "13111111111")

# DRF配置
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "common.utils.drf.pagination.PageNumberPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "PAGE_SIZE": 10,
    "EXCEPTION_HANDLER": "common.utils.drf.exceptions.exception_handler",
    "DEFAULT_FORMAT_SUFFIXES": '',  # 禁用格式后缀
}

"""
以下为框架代码 请勿修改
"""
# celery settings
# if IS_USE_CELERY:
#     INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
#     INSTALLED_APPS += ("django_celery_beat", "django_celery_results")
#     CELERY_ENABLE_UTC = False
#     CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
#
# # remove disabled apps
# if locals().get("DISABLED_APPS"):
#     INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
#     DISABLED_APPS = locals().get("DISABLED_APPS", [])
#
#     INSTALLED_APPS = [_app for _app in INSTALLED_APPS if _app not in DISABLED_APPS]
#
#     _keys = (
#         "AUTHENTICATION_BACKENDS",
#         "DATABASE_ROUTERS",
#         "FILE_UPLOAD_HANDLERS",
#         "MIDDLEWARE",
#         "PASSWORD_HASHERS",
#         "TEMPLATE_LOADERS",
#         "STATICFILES_FINDERS",
#         "TEMPLATE_CONTEXT_PROCESSORS",
#     )
#
#     import itertools
#
#     for _app, _key in itertools.product(DISABLED_APPS, _keys):
#         if locals().get(_key) is None:
#             continue
#         locals()[_key] = tuple(
#             [_item for _item in locals()[_key] if not _item.startswith(_app + ".")]
#         )
