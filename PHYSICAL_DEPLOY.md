# ITOps Platform 物理机部署指南

> **本部署方案完全不依赖 Docker**。所有服务直接运行在物理机上，使用 systemd 管理进程、MySQL 存储数据、Nginx 反向代理。
>
> **本项目有两个代码仓库：**
> - [wusdic/itops_platform](https://github.com/wusdic/itops_platform) — 开发版（含 Docker 开发环境）
> - [wusdic/itops-deploy](https://github.com/wusdic/itops-deploy) — 生产物理机部署版（本文档）

---

## 目录

- [系统要求](#系统要求)
- [架构概览](#架构概览)
- [快速部署（一键）](#快速部署一键)
- [手动分步部署](#手动分步部署)
  - [步骤1：安装系统依赖](#步骤1安装系统依赖)
  - [步骤2：配置 MySQL](#步骤2配置-mysql)
  - [步骤3：初始化数据库](#步骤3初始化数据库)
  - [步骤4：安装后端](#步骤4安装后端)
  - [步骤5：构建前端](#步骤5构建前端)
  - [步骤6：配置 Nginx](#步骤6配置-nginx)
  - [步骤7：注册 systemd 服务](#步骤7注册-systemd-服务)
  - [步骤8：验证部署](#步骤8验证部署)

---

## 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Ubuntu 22.04 LTS x86_64 |
| CPU | 2 核以上 |
| 内存 | 4GB 以上 |
| 磁盘 | 50GB 以上 |
| Python | 3.10+（自带，无需单独安装）|
| Node.js | 18.x |
| MySQL | 8.0 |
| Nginx | 最新版（apt 安装）|

---

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    物理机 (Bare Metal)                  │
│                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────┐  │
│  │   Nginx      │   │   MySQL 8    │   │  后端 API  │  │
│  │  (端口 80/443)│   │  (端口 3306) │   │ (端口 8000)│  │
│  └──────┬───────┘   └──────────────┘   └─────┬──────┘  │
│         │                                     │         │
│         │         ┌──────────────┐            │         │
│         └────────►│  静态文件    │◄───────────┘         │
│                  │  /opt/itops_platform/frontend/dist │
│                  └──────────────┘                     │
│                                                         │
│  ┌──────────────┐   ┌──────────────┐                   │
│  │   systemd    │   │  Python venv │                   │
│  │ itops-api    │   │  FastAPI/UVicorn              │  │
│  └──────────────┘   └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

**网络连接：** Nginx（80/443）→ 反向代理到 127.0.0.1:8000（后端 API）

---

## 快速部署（一键）

假设在干净的 Ubuntu 22.04 上，以 root 用户执行：

```bash
# 1. 克隆部署仓库
git clone https://github.com/wusdic/itops-platform.git /opt/itops-platform
cd /opt/itops-platform

# 2. 安装系统依赖（需要 root，会安装 MySQL/Nginx/Node.js）
sudo bash scripts/install_deps.sh

# 3. 配置环境变量（编辑 .env 填入数据库密码）
cp .env.example .env
nano /opt/itops_platform/.env
# 修改 ITOPS_DB_PASSWORD=YourSecurePassword

# 4. 执行一键部署
sudo bash scripts/deploy.sh
```

部署完成后访问：`http://服务器IP`

---

## 手动分步部署

### 步骤1：安装系统依赖

```bash
sudo bash scripts/install_deps.sh
```

该脚本会安装：
- MySQL Server 8.0
- Python 3 + venv + pip
- Node.js 18.x（通过 nodesource）
- Nginx
- 编译工具（build-essential, pkg-config, libmysqlclient-dev）

### 步骤2：配置 MySQL

```bash
# 启动 MySQL
sudo systemctl enable mysql
sudo systemctl start mysql

# 设置 root 密码（替换 YourSecurePassword）
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'YourSecurePassword';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

### 步骤3：初始化数据库

```bash
# 导入数据库初始化脚本（会创建 itops_platform 数据库和所有表）
mysql -u root -p'YourSecurePassword' < /opt/itops_platform/scripts/init_db.sql

# 验证数据库创建成功
mysql -u root -p'YourSecurePassword' -e "SHOW DATABASES;" | grep itops_platform
```

### 步骤4：安装后端

```bash
cd /opt/itops-platform/api

# 创建 Python 虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖（这一步耗时较长，约3-5分钟）
pip install --upgrade pip
pip install -r requirements.txt

deactivate
```

### 步骤5：构建前端

```bash
cd /opt/itops-platform/frontend

# 安装 Node 依赖
npm install --legacy-peer-deps

# 构建（产物输出到 dist/）
npm run build
```

### 步骤6：配置 Nginx

```bash
# 复制 Nginx 配置
sudo cp /opt/itops_platform/nginx/itops.conf /etc/nginx/sites-available/itops

# 启用站点（移除默认站点）
sudo ln -sf /etc/nginx/sites-available/itops /etc/nginx/sites-enabled/itops
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置并重载
sudo nginx -t
sudo systemctl reload nginx
```

### 步骤7：注册 systemd 服务

```bash
sudo bash /opt/itops_platform/scripts/install_service.sh

# 查看服务状态
sudo systemctl status itops-api

# 查看日志
sudo journalctl -u itops-api -f
```

### 步骤8：验证部署

```bash
# 验证 API 健康
curl -s http://localhost:8000/health

# 验证登录
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}'

# 验证前端（HTTP）
curl -s http://localhost/ | head -20
```

---

## 环境变量配置

部署前必须创建 `.env` 文件：

```bash
cp /opt/itops_platform/.env.example /opt/itops_platform/.env
nano /opt/itops_platform/.env
```

关键配置项：

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `ITOPS_DB_HOST` | MySQL 主机 | `localhost` |
| `ITOPS_DB_PORT` | MySQL 端口 | `3306` |
| `ITOPS_DB_NAME` | 数据库名 | `itops_platform` |
| `ITOPS_DB_USER` | 数据库用户 | `root` |
| `ITOPS_DB_PASSWORD` | 数据库密码 | `YourSecurePassword` |
| `JWT_SECRET` | JWT 签名密钥 | 随机字符串（至少32字符）|
| `API_HOST` | API 监听地址 | `0.0.0.0` |
| `API_PORT` | API 监听端口 | `8000` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `LOG_DIR` | 日志目录 | `/var/log/itops_platform` |

---

## 管理命令

```bash
# 查看服务状态
sudo systemctl status itops-api

# 重启服务
sudo systemctl restart itops-api

# 停止服务
sudo systemctl stop itops-api

# 查看实时日志
sudo journalctl -u itops-api -f

# 重新部署（拉取最新代码后）
sudo bash /opt/itops_platform/scripts/deploy.sh
```

---

## 目录结构

```
/opt/itops_platform/
├── api/                     # FastAPI 后端源码
│   ├── main.py              # API 入口
│   ├── requirements.txt     # Python 依赖
│   └── venv/               # Python 虚拟环境（部署后生成）
├── frontend/                # Vue3 前端源码
│   ├── dist/                # 构建产物（npm run build 后生成）
│   └── src/                 # 前端源代码
├── nginx/
│   └── itops.conf           # Nginx 配置文件
├── scripts/
│   ├── install_deps.sh      # 系统依赖安装
│   ├── init_db.sql          # 数据库初始化 SQL
│   ├── deploy.sh            # 一键部署脚本
│   └── install_service.sh   # systemd 服务注册
├── systemd/
│   └── itops-api.service    # systemd 服务文件
├── config/                   # 配置文件
├── modules/                  # 业务模块
├── .env                      # 环境变量（部署后生成，不提交）
└── .env.example              # 环境变量模板
```

---

## 默认账号

| 账号 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `Admin@123456` |

---

## 常见问题

### Q: 部署后访问显示 502 Bad Gateway

检查 Nginx 和后端服务状态：
```bash
sudo systemctl status nginx
sudo systemctl status itops-api
curl -s http://127.0.0.1:8000/health
```

### Q: MySQL 连接失败

确认 MySQL 已启动且密码正确：
```bash
sudo systemctl status mysql
mysql -u root -p'YourPassword' -e "SELECT 1;"
```

### Q: 前端修改后需要重新构建

```bash
cd /opt/itops-platform/frontend
npm install --legacy-peer-deps
npm run build
sudo systemctl restart itops-api
```

### Q: 如何更新到最新版本

```bash
cd /opt/itops-platform
git pull origin main
sudo bash scripts/deploy.sh
```

---

## CI/CD 自动发布

每次 push 到 `main` 分支，GitHub Actions 会自动：
1. 构建前端（Node.js 18）
2. 打包部署文件
3. 发布到 GitHub Release

下载最新部署包：
```bash
curl -L https://github.com/wusdic/itops-platform/releases/latest/download/itops_platform.tar.gz -o /tmp/itops.tar.gz
tar -xzf /tmp/itops.tar.gz -C /opt/
```
