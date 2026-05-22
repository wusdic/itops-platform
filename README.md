# ITOps Platform

企业级运维管理平台，支持设备监控、告警管理、工单系统、日志审计等功能。

## 快速部署

### 一键部署（推荐）

```bash
# 克隆代码
git clone https://github.com/wusdic/itops-deploy.git /opt/itops_platform
cd /opt/itops_platform

# 安装系统依赖（需要 root）
sudo bash scripts/install_deps.sh

# 填写环境配置
cp .env.example .env
nano .env   # 修改 ITOPS_DB_PASSWORD

# 执行部署
sudo bash scripts/deploy.sh
```

### 从 Release 下载（离线部署）

```bash
# 下载最新版本
curl -L https://github.com/wusdic/itops-deploy/releases/latest/download/itops_platform.tar.gz
tar -xzf itops_platform.tar.gz
cd itops_platform

# 配置并部署
sudo bash scripts/deploy.sh
```

## 系统要求

- Ubuntu 22.04 LTS
- MySQL 8.0
- Python 3.10+
- Node.js 18+
- Nginx

## 访问地址

- 前端：http://服务器IP
- API：http://服务器IP:8000
- API 文档：http://服务器IP:8000/docs

## 默认账号

- 用户名：`admin`
- 密码：`Admin@123456`

## 管理命令

```bash
# 查看服务状态
sudo systemctl status itops-api

# 重启服务
sudo systemctl restart itops-api

# 查看日志
sudo journalctl -u itops-api -f

# 重新部署
sudo bash /opt/itops_platform/scripts/deploy.sh
```

## 目录结构

```
itops_platform/
├── api/                    # FastAPI 后端
├── frontend/               # Vue3 前端
│   └── dist/              # 构建产物（部署时使用）
├── nginx/                  # Nginx 配置
├── scripts/                # 部署脚本
├── systemd/                # systemd 服务文件
├── modules/                # 业务模块
├── config/                 # 配置文件
└── docs/                  # 文档
```

## 开发

```bash
# 前端开发
cd frontend
npm install
npm run dev

# 后端开发
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## CI/CD

每次 push 到 main 分支会自动构建并发布 Release。

## 文档

- [物理机部署指南](./PHYSICAL_DEPLOY.md) — 完整的物理机部署说明
