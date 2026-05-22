#!/bin/bash
# ============================================================
# ITOps Platform - 系统依赖安装脚本（物理机部署）
# 适用系统：Ubuntu 22.04 LTS
# 运行方式：sudo bash install_deps.sh
# ============================================================
set -e

echo "=== ITOps Platform 依赖安装（物理机） ==="

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    echo "错误：请使用 root 用户运行"
    echo "或使用: sudo bash $0"
    exit 1
fi

echo "[1/6] 更新系统包..."
apt update

echo "[2/6] 安装 MySQL Server 8.0..."
apt install -y mysql-server mysql-client

echo "[3/6] 安装 Python 环境..."
apt install -y python3 python3-venv python3-pip python3-dev pkg-config

echo "[4/6] 安装编译依赖和系统工具..."
apt install -y default-libmysqlclient-dev build-essential curl wget git

echo "[5/6] 安装 Node.js 18.x..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
else
    echo "Node.js 已安装: $(node -v)"
fi

echo "[6/6] 安装 Nginx..."
apt install -y nginx

# 启用并启动 MySQL
echo ""
echo "=== 配置 MySQL ==="
systemctl enable mysql
systemctl start mysql
echo "MySQL 状态: $(systemctl is-active mysql)"

echo ""
echo "=== 安装完成 ==="
echo "下一步："
echo "  1. cp .env.example .env && nano .env  # 填写数据库密码"
echo "  2. bash scripts/deploy.sh             # 执行部署"
