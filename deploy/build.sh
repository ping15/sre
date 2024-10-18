#!/bin/bash

########## 目标机器构建缓慢，所以采用本地构建镜像后同步到目标机器上，脚本执行或许有些镜像缺失，自行补上即可 ##########
# 设置变量
## 目标机器IP
REMOTE_SERVER=

## 目标机器
REMOTE_DIR="~/sre-docker"

## 目标机器密码
PASSWORD=

## 本地镜像包文件名
DOCKER_IMAGE_NAME="training-center_web"
DOCKER_IMAGE_TAR="${DOCKER_IMAGE_NAME}.tar"


# 检查参数是否包含 "local"
IS_LOCAL=false
if [[ "$1" == "local" ]]; then
  IS_LOCAL=true
fi

# 检查是否安装了 sshpass，如果没有则安装
if ! command -v sshpass &> /dev/null; then
  echo "sshpass 未安装，正在安装..."
  sudo apt-get update
  sudo apt-get install -y sshpass
fi

# 执行 docker-compose down
echo "停止并移除 Docker 容器..."
docker-compose down

# 执行 docker-compose up --build -d
echo "构建并启动 Docker 容器..."
docker-compose up --build -d

# 判断是否是 local 模式，如果是，则结束脚本
if $IS_LOCAL; then
  echo "本地模式，脚本执行完毕！"
  exit 0
fi

# 执行 docker save
echo "保存 Docker 镜像到 tar 文件..."
docker save -o $DOCKER_IMAGE_TAR $DOCKER_IMAGE_NAME

# 使用 sshpass 执行 rsync，将当前目录的所有文件（排除特定目录）复制到远程服务器
echo "将当前目录的所有文件（排除特定目录）复制到远程服务器..."
sshpass -p $PASSWORD rsync -av --exclude='training-center-api' --exclude='training-center-front' ./ $REMOTE_SERVER:$REMOTE_DIR

# 在远程服务器上执行 Docker 命令
echo "在远程服务器上执行 Docker 命令..."
sshpass -p $PASSWORD ssh $REMOTE_SERVER << EOF
cd $REMOTE_DIR
docker-compose down
docker rmi $DOCKER_IMAGE_NAME
docker load -i $DOCKER_IMAGE_TAR
docker-compose up -d
EOF

echo "脚本执行完毕！"
