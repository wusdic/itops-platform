# ITOps Platform

企业级 IT 运维管理平台 — **设备发现 → 设备纳管 → 监控告警 → 工单处理 → AI 辅助决策**。

## 5 分钟了解

| 维度 | 说明 |
|------|------|
| **是什么** | 私有化部署的运维平台，支持自动化采集、智能告警、工单闭环、AI 辅助 |
| **技术栈** | Vue 3 + FastAPI + MySQL + Redis + Qwen3.5 本地 LLM |
| **核心能力** | IP 扫描发现 /  SNMP + SSH 采集 / 阈值告警 / SLA 工单 / 本地 AI 分析 |
| **部署方式** | 物理机（systemd） 或 Docker |
| **实现程度** | ~87%（184 项需求中已实现 160 项） |

## 快速开始

### 一键部署（推荐）

```bash
git clone https://github.com/wusdic/itops-platform.git /opt/itops-platform
cd /opt/itops-platform
sudo bash scripts/install_deps.sh    # 安装 MySQL/Nginx/Node.js
cp .env.example .env && nano .env     # 修改 ITOPS_DB_PASSWORD
sudo bash scripts/deploy.sh          # 一键部署
```

访问 **http://服务器IP** → 登录 `admin` / `Admin@123456`

### 开发模式

```bash
# 后端
cd api && source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# 前端（另一个终端）
cd frontend && npm install && npm run dev
```

### AI 服务（可选）

```bash
bash start_llm_server_35.sh   # 启动 Qwen3.5-0.8B（端口 11436）
```

## 核心功能

### 设备管理闭环

```
IP段扫描 → ARP/SNMP 发现 → 指纹识别类型 → 批量导入 → 定时采集监控
```

### 告警 → 工单闭环

```
指标采集 → 阈值触发 → 告警收敛 → 自动派单 → SLA 计时 → 多级审批 → 案例归档
         ↓
    AI 根因分析 + 处置建议
```

### 自动化运维

```
定时任务（Crontab）→ 脚本执行 → 巡检报告 → 失败自动回滚
```

## 目录结构

```
itops_platform/
├── api/                    # FastAPI 后端
│   ├── routes/             # API 路由（21 个文件，650+ 端点）
│   ├── dependencies.py     # 公共依赖（分页/认证）
│   └── main.py             # 应用入口 + lifespan
├── modules/
│   ├── business/           # 业务逻辑（monitoring/workorder/knowledge/ai...）
│   ├── collection/         # 采集模块（snmp/ssh/api/discovery）
│   └── foundation/         # 基础层（db_models/auth/sharding）
├── frontend/src/
│   ├── views/              # 页面（20+ 个业务视图）
│   └── api/                # 前端 API 调用（20 个文件）
├── config/                 # 配置文件（YAML）
├── deploy/                 # Docker/Nginx 部署配置
├── docs/                   # 设计文档
└── scripts/                # 部署脚本
```

## 文档导航

| 文档 | 用途 |
|------|------|
| **[DESIGN.md](./DESIGN.md)** | 架构设计、模块详解、核心流程 |
| **[IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)** | 各模块实现状态、遗留问题 |
| **[SPEC.md](./SPEC.md)** | 技术规范（枚举/字段/API 契约） |
| **[CHANGES.md](./CHANGES.md)** | 代码变更历史 |
| **[/docs](./docs/)** | 详细设计文档（架构/SRS/测试标准） |

## 系统要求

| 项目 | 最低要求 |
|------|----------|
| CPU | 2 核 |
| 内存 | 4 GB |
| 磁盘 | 50 GB |
| OS | Ubuntu 22.04 LTS |
| MySQL | 8.0 |
| Node.js | 18+ |
| Python | 3.10+ |

## 默认端口

| 服务 | 端口 |
|------|------|
| 前端（Nginx） | 80 |
| API（FastAPI） | 8000 |
| API Docs | 8000/docs |
| Redis | 6379 |
| MySQL | 3306 |
| MinIO | 9000 |
| LLM（llama.cpp） | 11436 |

## 常见问题

**Q: 服务启动后无法访问？**  
服务重启后需等待 ~10s 才能响应。执行 `curl http://localhost:8000/api/v1/auth/login` 验证。

**Q: 前端页面空白？**  
检查浏览器控制台（DevTools → Console），常见原因是 API 路径不匹配。先 `curl http://localhost:8000/api/v1/auth/login` 确认后端正常。

**Q: AI 功能不可用？**  
确认 LLM 服务运行中：`curl http://localhost:11436` 有响应。若未部署 AI，平台其余功能完全可用。

## 参与贡献

1. Fork → Feature Branch → PR
2. 代码必须符合 `SPEC.md` 规范
3. 新功能先更新 `DESIGN.md` + `IMPLEMENTATION_STATUS.md`
4. 所有 API 变更必须更新 `/docs`

## License

Private Project — Internal Use Only
