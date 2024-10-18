# 第一阶段：构建前端应用
FROM node:18.20.4 as build-stage

# 设置工作目录
WORKDIR /training-center-front

# 复制 package.json 和 yarn.lock
COPY training-center-front/package.json training-center-front/yarn.lock ./

# 设置 npm 的 registry 为腾讯的镜像
RUN npm config set registry https://mirrors.tencent.com/npm/

# 安装依赖
RUN yarn install

# 复制全部源代码到工作目录
COPY training-center-front/ .

RUN chmod +x /training-center-front/node_modules/.bin/vite

# 构建项目
RUN npm run build

# 替换 index.html 中的路径
RUN sed -i 's|./assets|/media/assets|g' /training-center-front/dist/index.html

# 第二阶段：构建后端应用
#FROM python:3.8.10
FROM python:3.8.11-slim-bullseye

# 设置工作目录
WORKDIR /training-center-api

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to ensure you have the latest version
RUN pip install --upgrade pip

# 复制后端的 requirements.txt 并安装依赖
COPY training-center-api/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# 复制后端的全部源代码到工作目录
COPY training-center-api/ .

# 从前端构建阶段复制构建的文件到后端的适当位置
COPY --from=build-stage /training-center-front/dist/index.html /training-center-api/home_application/templates/home_application/index.html
RUN mkdir -p /training-center-api/media
COPY --from=build-stage /training-center-front/dist/assets /training-center-api/media/assets

# 安装 supervisord
RUN apt-get update && apt-get install -y supervisor

# 复制 supervisord 配置文件
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 设置启动命令
CMD ["/usr/bin/supervisord"]
