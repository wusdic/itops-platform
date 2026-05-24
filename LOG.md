# ITOps Platform 开发记录

> 最后更新：2026-05-23

## 服务状态

- **API 服务**：PID 3128822，端口 8000
- **前端构建**：`frontend/dist/`（已更新）
- **数据库**：MySQL itops_platform @ localhost:3306
- **Redis**：localhost:6379（db=1）
- **LLM**：localhost:11435，Qwen3.5-0.8B-Q4_K_M.gguf
- **默认账号**：admin / Admin@123456

## P0 功能（已全部实现 ✅）

| 任务 | 描述 | 验证方式 |
|---|---|---|
| P0-1 | API Key 认证 | `verify_api_key()` 在 `api/middleware/auth.py` |
| P0-2 | 告警转派 | `POST /alerts/{id}/transfer` |
| P0-3 | 告警屏蔽 | `POST /alerts/{id}/suppress` |
| P0-4 | 工单草稿保存 | `WorkOrderDraftManager` 在 `modules/business/workorder/draft_manager.py` |
| P0-5 | AI Copilot 对话 | `POST /ai/copilot/chat` |
| P0-6 | 设备指纹模板版本 | `GET /credentials/versions` |
| P0-7 | 导出数据权限 | admin 权限中间件 |
| P0-8 | 数据脱敏展示 | YAML credentials 脱敏 |

## P1 功能（已全部实现 ✅）

| 任务 | 描述 | 关键文件 |
|---|---|---|
| P1-9 | 审批流程可视化 | `api/routes/workorder.py` + `frontend/workorder/list.vue` |
| P1-10 | 自定义仪表盘布局 | `PUT/GET /dashboard/layout` + `dashboard/index.vue` |
| P1-11 | LDAP SSO 单点登录 | `POST /ldap-login` + `GET /ldap/status`（auth.py:496-646）|
| P1-12 | 系统备份恢复 | `GET /admin/backup`（admin.py）|
| P1-13 | 配置热更新 | `init_config_hot_reload()`（main.py:86）+ `ConfigManager.start_watching()` |
| P1-14 | 运维知识库 SOP | `kb_categories` + `kb_sop_documents` + `kb_document_reviews` 三表 |
| P1-15 | LLM 模型降级策略 | `llm_client.py` 降级链路（OpenAI → Ollama → Mock）|
| P1-16 | 相似案例 AI 复用推荐 | `CaseRecommender`（case.py:758-917）+ `POST /fault-case/{id}/recommend-similar` |
| P1-17 | 日志配置管理 | `GET/PUT /admin/log-configs` |
| P1-18 | 告警增强字段 | `AlertRecord.last_escalated_at` + `AlertTrigger.check_escalation()` |

## P2 功能

| 任务 | 描述 | 状态 |
|---|---|---|
| P2-19 | ARP 主动扫描 | ✅ `ARPScanner` 类（scanner.py）+ `POST /discovery/arp/scan` |
| P2-20 | 知识图谱检索 | ❌ 需要 Neo4j，暂跳过 |
| P2-21 | 执行失败自动回滚 | ✅ `RollbackManager`（rollback.py:524行）+ rollback API |
| P2-22 | 组织架构管理 | ✅ `Department` 模型 + 6个 CRUD API + 树形接口 |
| P2-23~27 | 多租户/分表/滚动升级/数字水印 | ❌ 架构全局改造，风险高，跳过 |

## 已验证的后端能力（代码存在但旧版 GAP_ANALYSIS 漏标）

| 项目 | 描述 | 位置 |
|---|---|---|
| MAIN-001 | 配置热更新 | `core/config/manager.py:84` `ConfigManager.start_watching()` |
| MON-022 | 告警屏蔽 | `monitoring.py:1300` `POST /alerts/{id}/suppress` |
| MON-024 | 告警升级定时任务 | `alerter.py:561-746` `AlertTrigger._escalation_loop()` |

## 遗留缺口

- **P2-20 知识图谱**：依赖 Neo4j，当前环境不可用
- **P2-23~27**：多租户/分表/滚动升级/数字水印/滚动发布，均为全局架构改造，需谨慎评估

## 重要调试经验

### 服务重启时机
新增 SQLAlchemy Model 后必须重启 uvicorn，否则 `Base.metadata.create_all` 不会注册新表。

### 路由注册顺序
FastAPI 按定义顺序匹配，动态路径（如 `/{id}`）必须放在静态路径（如 `/tree`）之后。

### LLM 连接
- 本地 ollama 默认端口 **11434**（不是 11435）
- `LLMClient()` 无参数调用会得到 `llm_client = None`，需在调用前检查
- `chat()` 接收 `List[Dict]`（消息列表），不是字符串 prompt

### ARP 扫描
- root 用户：原始套接字（需 `CAP_NET_RAW`）
- 非 root：读取 `/proc/net/arp`（缓存，非实时）
- 内置 OUI 数据库 109 条

### Dashboard Layout
- 后端 `DashboardLayoutPersistence` 在 `modules/business/dashboard/persistence.py`
- 前端 `dashboard/index.vue` 需从 API 加载 layout 并动态渲染
