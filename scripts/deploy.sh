#!/bin/bash
# ============================================================
# ITOps Platform - 一键部署脚本
# 用法: bash deploy.sh [release_tag]
#   release_tag: 可选，如 latest，不填则从 git pull 最新代码
# ============================================================
set -e

APP_DIR="/opt/itops_platform"
TAG="${1:-}"

echo "=== ITOps Platform 部署脚本 ==="
echo "工作目录: $APP_DIR"
echo ""

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    echo "错误：请使用 root 用户运行此脚本"
    echo "或使用: sudo bash $0"
    exit 1
fi

# 创建应用目录
mkdir -p $APP_DIR

# ============================================================
# 从 GitHub 下载并解压，或从本地构建
# ============================================================
if [ -n "$TAG" ]; then
    echo "[1/7] 从 GitHub Release $TAG 下载..."
    RELEASE_URL="https://github.com/wusdic/itops-deploy/releases/download/${TAG}/itops_platform.tar.gz"
    curl -L "$RELEASE_URL" -o /tmp/itops_platform.tar.gz
    tar -xzf /tmp/itops_platform.tar.gz -C $APP_DIR --strip-components=1
    rm /tmp/itops_platform.tar.gz
else
    echo "[1/7] 从 GitHub 克隆最新代码..."
    if [ -d "$APP_DIR/.git" ]; then
        cd $APP_DIR && git pull origin main
    else
        git clone https://github.com/wusdic/itops-deploy.git $APP_DIR --depth=1
    fi
fi

# ============================================================
# 配置环境变量
# ============================================================
echo "[2/7] 配置环境变量..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo "请编辑 $APP_DIR/.env 填写数据库密码等配置"
    echo "完成后重新运行此脚本: bash $APP_DIR/scripts/deploy.sh"
    exit 1
fi

# 加载 .env
set -a
source $APP_DIR/.env
set +a

# ============================================================
# 初始化数据库
# ============================================================
echo "[3/7] 初始化数据库..."
mysql -u root -p"${ITOPS_DB_PASSWORD}" < $APP_DIR/scripts/init_db.sql 2>/dev/null || \
mysql -u root < $APP_DIR/scripts/init_db.sql

# ============================================================
# 构建前端
# ============================================================
echo "[4/7] 构建前端..."
cd $APP_DIR/frontend
npm install --legacy-peer-deps
npm run build
cd ..

# ============================================================
# 安装后端依赖
# ============================================================
echo "[5/7] 安装后端依赖..."
cd $APP_DIR/api
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

# ============================================================
# 配置 Nginx
# ============================================================
echo "[6/7] 配置 Nginx..."
cp $APP_DIR/nginx/itops.conf /etc/nginx/sites-available/itops
ln -sf /etc/nginx/sites-available/itops /etc/nginx/sites-enabled/itops
rm -f /etc/nginx/sites-enabled/default  # 移除默认站点
nginx -t && systemctl reload nginx

# ============================================================
# 注册 systemd 服务
# ============================================================
echo "[7/7] 注册 systemd 服务..."
bash $APP_DIR/scripts/install_service.sh

# 重启服务
systemctl daemon-reload
systemctl restart itops-api
systemctl status itops-api --no-pager

echo ""
echo "=== 部署完成 ==="
echo "访问地址: http://$(hostname -I | awk '{print $1}')"
echo "API 地址: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "管理命令:"
echo "  查看状态: systemctl status itops-api"
echo "  重启服务: systemctl restart itops-api"
echo "  查看日志: journalctl -u itops-api -f"
