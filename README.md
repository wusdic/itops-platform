# ITOPS 平台

> 面向私有化部署场景的自治运维操作系统。

## 文档

**所有开发依据请参考：[docs/00-overview/README.md](./docs/00-overview/README.md)**

快速链接：
- [架构总纲](./docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md)
- [详细开发计划](./docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md)

## 技术栈

- **前端**：Vue 3 + TypeScript + Vite + Pinia + Element Plus
- **后端**：Python 3.10+ + FastAPI + SQLAlchemy 2.0 + Pydantic V2
- **数据库**：MySQL 8.0
- **缓存/队列**：Redis
- **AI**：Ollama / vLLM（本地 LLM）

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 API 服务
bash run.sh

# 访问
# 前端：http://localhost:5173
# API：http://localhost:8000
```

## 默认账号

- 用户名：`admin`
- 密码：`Admin@123456`

## 项目结构

```
├── api/              # FastAPI 路由和入口
├── core/             # 核心模块
├── modules/          # 业务模块
│   ├── business/     # 业务逻辑
│   ├── collectors/   # 采集器
│   └── foundation/   # 基础设施
├── frontend/         # Vue 3 前端
├── docs/             # 文档（见 docs/00-overview/README.md）
├── deploy/           # 部署配置
└── tests/            # 测试
```

## 开发文档

详见 [docs/00-overview/README.md](./docs/00-overview/README.md)
