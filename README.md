## 本地开发
### 1. 前端
#### 1.1. 修改前端代码所有默认写死的后端代理，搜8001，将搜到的:左右两边的ip和端口替换为本地的后端服务器ip和端口
#### 1.2. yarn install
#### 1.3. yarn run dev启动前端服务器
### 2. 后端
#### 2.1. 本地主目录新建local_settings.py配置 DATABASES 和 CACHES
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "training-center-test",
        "USER": "root",
        "PASSWORD": "root",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {"charset": "utf8mb4"},
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
    'login_db': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'account_cache'
    },
}

```
#### 2.2. python manage.py ensure_db_and_migrate迁移数据库，不存在会自动创建
#### 2.3. 注入环境变量
```text
# COS配置
# COS_SECRET_ID=
# COS_SECRET_KEY=
# COS_REGION=
# COS_BUCKET=

# SMS配置
# SMS_USERNAME=
# SMS_PASSWORD=

# ensure_db_and_migrate初始化数据库时第一个用户手机号，身份为超级管理员，默认为13111111111
# ADMIN_PHONE=

# 是否启用，不启用注释掉就可以了
# ENABLE_SMS=true
```
#### 2.4. python manage.py runserver启动服务器

## 线上docker部署
### 1. 创建文件夹，按下面结构组装
- Dockerfile(来源于后端仓库deploy文件夹)
- build.sh(来源于后端仓库deploy文件夹)
- docker-compose.yml(来源于后端仓库deploy文件夹)
- supervisord.conf(来源于后端仓库deploy文件夹)
- training-center-api(后端代码仓库)
- training-center-front(前端代码仓库)

### 2. 在当前文件夹目录中执行bash build.sh
