#!/bin/bash
# ============================================================
# ITOps Platform - 系统依赖安装脚本
# 适用系统：Ubuntu 22.04 LTS
# 运行方式：sudo bash install_deps.sh
# ============================================================
set -e

echo "=== ITOps Platform 依赖安装 ==="

# 更新 apt 源
echo "[1/6] 更新系统包..."
apt update

# 安装 MySQL
echo "[2/6] 安装 MySQL Server..."
apt install -y mysql-server mysql-client

# 安装 Python 和 venv
echo "[3/6] 安装 Python 环境..."
apt install -y python3 python3-venv python3-pip python3-dev pkg-config

# 安装系统依赖（MySQL client library 等）
echo "[4/6] 安装编译依赖..."
apt install -y default-libmysqlclient-dev build-essential curl

# 安装 Node.js 18.x
echo "[5/6] 安装 Node.js 18.x..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
else
    echo "Node.js 已安装: $(node -v)"
fi

# 安装 Nginx
echo "[6/6] 安装 Nginx..."
apt install -y nginx

# 启用并启动 MySQL
echo ""
echo "=== 配置 MySQL ==="
systemctl enable mysql
systemctl start mysql
echo "MySQL 状态: $(systemctl is-active mysql)"

# 创建 Python venv 目录（不在此处创建 venv，等 deploy.sh）
echo ""
echo "=== 安装完成 ==="
echo "下一步：运行 deploy.sh 进行部署"
