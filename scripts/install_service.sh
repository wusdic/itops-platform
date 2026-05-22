#!/bin/bash
# ============================================================
# ITOps Platform - 注册 systemd 服务
# ============================================================
set -e

APP_DIR="/opt/itops_platform"

if [ "$EUID" -ne 0 ]; then
    echo "错误：请使用 root 用户运行"
    exit 1
fi

echo "=== 注册 itops-api systemd 服务 ==="

# 复制 service 文件
cp $APP_DIR/systemd/itops-api.service /etc/systemd/system/itops-api.service

# 重新加载 systemd
systemctl daemon-reload

# 启用服务（开机自启）
systemctl enable itops-api

echo "服务已注册并设置为开机自启"
echo "当前状态:"
systemctl status itops-api --no-pager
