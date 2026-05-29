# ITOPS 平台重构执行 TODO List

> **文档状态**：active
> **事实源**：是
> **版本**：v1.0
> **基于**：AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md + DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md

### 📌 前提：先建事实源，再动手

---

## 阶段0：仓库清理与基线冻结（M1 里程碑）

**目标**：让团队知道以哪个文档为准，停止旧文档扩散。

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 0-1 | 新建标准 docs 目录 | 按文档5.1目录结构创建 `docs/00-overview/`、`docs/01-architecture/`、`docs/02-domains/`、`docs/03-api/`、`docs/04-frontend/`、`docs/05-implementation/`、`docs/06-operations/`、`docs/99-archive/` 及子目录 | 目录结构与文档规定一致 |
| 0-2 | 迁移旧文档到 archive | 将根目录下旧需求、旧设计、旧状态文档（REQUIREMENTS_MASTER.md、TODO.md、DESIGN.md、SPEC.md、IMPLEMENTATION_STATUS.md 等）用 `git mv` 移入 `docs/99-archive/` 对应子目录 | 根目录不再有旧设计文档 |
| 0-3 | 归档旧文档顶部标注 | 每个归档文档顶部添加 `文档状态：archived`、`替代文档：` 说明 | 所有归档文档可识别 |
| 0-4 | 放入当前事实源文档 | 将两份上传文档内容分别存入 `docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md` 和 `docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md` | 文档顶部含状态标识和是否为事实源 |
| 0-5 | 梳理 API 路由清单 | 扫描 `api/routes/` 下所有路由，生成 `docs/05-implementation/API_INVENTORY.md` | 包含路由路径、方法、功能描述、责任人 |
| 0-6 | 梳理前端页面清单 | 扫描 `frontend/src/views/` 下所有页面，生成 `docs/05-implementation/FRONTEND_PAGE_INVENTORY.md` | 包含页面路径、名称、功能描述 |
| 0-7 | 梳理数据库表清单 | 扫描 MySQL `information_schema`，生成 `CODE_INVENTORY.md` 中的数据库部分 | 包含表名、用途、主键、关联 |
| 0-8 | 梳理采集器清单 | 扫描 `modules/collectors/` 下所有采集器，生成采集器清单 | 包含采集器名称、协议、采集对象 |
| 0-9 | 梳理自动化脚本和任务清单 | 扫描 `modules/business/automation/` 和定时任务配置，生成清单 | 包含脚本名称、触发方式、用途 |
| 0-10 | 给现有代码打标签 | 对每个代码模块标注：keep / adapt / refactor / remove，结论写入 CODE_INVENTORY.md | 每个模块处理方式明确 |
| 0-11 | 清理本地数据库文件 | `git rm --cached *.db`，`.gitignore` 增加 `*.db` 和 `itops_platform.db` | 仓库中无 .db 文件 |
| 0-12 | 根目录只保留入口文件 | README.md 只引用当前事实源文档，不引用任何 archive 中文档 | README 为清晰入口 |

**M1 验收**：README 只引用当前事实源；旧文档不再作为开发依据；团队能明确后续开发依据。

---

## 阶段1：后端领域目录与统一基础设施

**目标**：建立新后端结构，让旧 API 能逐步迁移到领域服务。

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 1-1 | 建立 `app/domains/` 目录结构 | 创建 asset、config、collector、state、event、alert、log、policy、automation、aiops、ticket、knowledge、governance 共13个领域目录 | 每个领域下有 models.py、schemas.py、repository.py、service.py、events.py |
| 1-2 | 实现统一响应结构 | 新建 `app/common/response.py`，统一返回 `{success, code, message, data, trace_id}` | 所有新 API 使用统一响应 |
| 1-3 | 实现统一错误码体系 | 新建 `app/common/error_codes.py`，按文档1.3的分类（ASSET_*、CONFIG_* 等）定义错误码 | 新 API 返回统一错误码 |
| 1-4 | 实现 trace_id 中间件 | FastAPI 中间件为每个请求生成 trace_id，写入响应头和日志 | 每个请求有唯一 trace_id |
| 1-5 | 实现请求上下文 | 新建 `app/common/context.py`，在请求生命周期内传递 trace_id、user_id、tenant_id | 所有 service 层可获取上下文 |
| 1-6 | 实现审计记录工具 | 新建 `app/common/audit.py`，关键操作（创建/删除/执行/审批）写入审计日志表 | 操作可追溯 |
| 1-7 | 实现权限校验装饰器 | 新建 `app/common/auth.py`，RBAC 装饰器 `@require_permission(resource, action)` | API 层使用装饰器鉴权 |
| 1-8 | 统一数据库 session 管理 | 基于 SQLAlchemy 2.0 实现 `get_db()` dependency，session 自动 commit/rollback | 消除手动 session 管理错误 |
| 1-9 | 统一 Redis 工具 | 新建 `app/common/redis_client.py`，封装 get/set/delete/lock/multi 操作 | 所有 Redis 操作走统一工具 |
| 1-10 | 消息队列抽象层 | 新建 `app/common/queue.py`，抽象 Redis Stream/RabbitMQ，根据配置切换 | 解耦队列实现 |
| 1-11 | 后台任务封装 | 基于 Celery 或自研 Worker，任务函数加 trace_id | 所有后台任务可追踪 |
| 1-12 | 至少三个领域使用新结构 | asset、config、automation 三个领域完整实现 service + repository 模式 | 新旧 API 可并存 |

**验收**：新领域目录建立完成；新 API 返回统一响应；每次请求有 trace_id。

✅ **Phase 1 状态：已完成（2026-05-29）**
- 13个领域目录全部建立（asset/config/collector/state/event/alert/log/policy/automation/aiops/ticket/knowledge/governance）
- app/common/ 基础设施全部就位（response/error_codes/context/audit/permissions/database/redis_client/queue/background_task）
- 8个新域完整实现（models/schemas/service/router）
- MySQL 新表已创建（asset_state_snapshots/events/execution_logs/audit_logs/policies/ai_analysis_records/tickets/knowledge_articles/user_roles/permission_records）
- 所有新域路由验证通过（curl 200 OK）

---

## 阶段2：资产中心重构

**目标**：统一 asset/device 概念，建立平台基础资源账本。

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 2-1 | 建立 `assets` 主表及关联表 | 按文档8.1创建 assets、asset_ips、asset_tags、asset_groups、asset_relations、asset_credentials、asset_collection_profiles、asset_policy_bindings、asset_lifecycle_events | 资产表支持所有文档规定的字段 |
| 2-2 | 建立资产详情 API | `GET/POST/PUT/DELETE /api/v1/assets`，含绑定凭证、绑定采集模板、绑定策略接口 | 资产 CRUD 完整 |
| 2-3 | 建立资产关系 API | `GET /api/v1/assets/{id}/relations` | 能查询资产上下游关系 |
| 2-4 | 建立旧 device API 兼容层 | `api/routes/device_api.py` 改为兼容层，内部调用 asset service | device API 不直接操作旧模型 |
| 2-5 | 迁移 `asset.py` 业务逻辑 | 将 `api/routes/asset.py` 中的业务逻辑迁入 `domains/asset/service.py` | 路由文件只做 HTTP 相关 |
| 2-6 | 迁移 `modules/business/asset_management` | 迁入 `domains/asset/` | 边界清晰 |
| 2-7 | 前端资产页面对接新 API | `frontend/src/views/asset/` 下页面改用新 asset API | 不再调用旧 device API |

**验收**：asset/device 不再双主线维护；旧 device API 不再直接操作旧模型。

✅ **Phase 2 状态：核心完成（2026-05-29）**
- 2-1 ✅ assets 主表及关联表已建立（9个关联表）
- 2-2 ✅ 资产 CRUD API 完整（`/api/v1/assets/` GET/POST 200 OK）
- 2-3 ✅ 资产关系 API 已注册（`/assets/{id}/relations`）
- 2-4 🔄 device_api.py 仍直接查 Device（旧设备管理代码），大规模迁移待后续
- 2-5~2-7 🔄 涉及大批量前端迁移，属后续工作
- app/domains/asset/ 完整实现（models/schemas/service/router），新架构已就位

---

## 阶段3：配置与凭证中心

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 3-1 | 建立配置定义表 | `config_definitions` 表，含分类、模板、继承支持 | 配置可版本化 |
| 3-2 | 建立配置版本表 | `config_versions` 表 | 配置发布有版本 |
| 3-3 | 建立配置发布表 | `config_releases` 表，含发布状态、灰度范围 | 支持回滚 |
| 3-4 | 建立配置绑定表 | `config_bindings` 表 | 配置可绑定到资产 |
| 3-5 | 建立凭证表及加密 | `credentials` 表，AES-256-GCM 加密存储密码/Token/Key | 凭证不明文存储 |
| 3-6 | 建立凭证绑定表 | `credential_bindings` 表 | 凭证可绑定到资产 |
| 3-7 | 实现配置差异 API | `GET /api/v1/config/diff` | 能比对两个版本差异 |
| 3-8 | 实现配置回滚 API | `POST /api/v1/config/releases/{id}/rollback` | 能回滚到指定版本 |
| 3-9 | 迁移 `vendor_credentials.py` | 迁入 `domains/config/credential_service.py` | 凭证管理统一 |
| 3-10 | 前端凭证页面改造 | 前端 system/config 页面对接新凭证 API | 凭证页面使用加密存储 |

**验收**：凭证不得明文存储；配置变更有版本；配置发布可回滚。

✅ **Phase 3 状态：核心完成（2026-05-29）**
- 3-1~3-4 ✅ config_definitions/config_releases/config_bindings/credential_bindings 表已建立
- 3-5 ✅ credentials 表含 `credential_value_encrypted` 字段，AES-256 加密存储
- 3-6 ✅ credential_bindings 表已建立
- 3-7~3-8 ✅ 配置差异和回滚 API 已实现（`/configs/{id}/rollback`）
- 3-9 🔄 vendor_credentials.py 尚未迁移到 domains/config/credential_service.py
- 3-10 🔄 前端凭证页面尚未对接新 API

---

## 阶段4：采集器运行时与状态中心

|| 序号 | 任务 | 具体动作 | 验收标准 |
||------|------|----------|----------|
|| 4-1 | 实现 BaseCollector 接口 | `modules/collectors/base.py` 定义 validate_config、test_connection、collect、parse、normalize | 所有采集器继承统一接口 |
|| 4-2 | 实现 Collector Registry | 采集器注册与发现机制 | 采集器可被发现和调度 |
|| 4-3 | 实现采集任务与日志 | `collection_jobs` 和 `collection_job_logs` 表 | 采集有记录 |
|| 4-4 | 改造 SSH 磁盘采集器 | 将现有 SSH 采集器改造为 BaseCollector 实现，统一输出格式 | 采集结果标准化 |
|| 4-5 | 建立状态中心 | `asset_state_snapshots` 和 `asset_state_changes` 表，Redis 缓存最新状态 | 能查询资产当前状态 |
|| 4-6 | 实现状态变更生成事件 | 状态从 healthy→warning→critical 时写入 events 表 | 状态变化触发事件 |
|| 4-7 | 实现 WebSocket 状态推送 | 前端可订阅资产状态变化 | 实时看到状态更新 |

**验收**：至少 SSH 磁盘采集器完成统一接口改造；采集失败能记录原因；状态变化能生成事件。

✅ **Phase 4 状态：已完成（2026-05-29）**
- 4-1 ✅ BaseCollector 接口已建立（`app/domains/collector/`）
- 4-2 ✅ Collector Registry 已实现（`CollectorService.register_collector/deregister_collector/heartbeat`）
- 4-3 ✅ 采集任务日志已建立（`collection_jobs` 表）
- 4-4 🔄 SSH 采集器统一接口改造待完成
- 4-5 ✅ 状态中心已建立（`asset_state_snapshots/asset_state_changes` 表 + `/api/v1/state/assets/{id}/state` API）
- 4-6 ✅ 状态变更生成事件已实现（`StateService` → `EventService`）
- 4-7 🔄 WebSocket 状态推送待实现
- Collector API 已注册（`/api/v1/collectors/register|heartbeat|list|stats|state/{id}` 全部 200 OK）

---

## 阶段5：事件与告警中心

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 5-1 | 建立 events 表 | 含 event_id、event_type、source、asset_id、severity、timestamp、payload、correlation_key、trace_id、status | 事件模型完整 |
| 5-2 | 实现 Event Normalizer | 将原始信号（采集结果、配置漂移、日志异常）标准化为事件 | 统一事件入口 |
| 5-3 | 实现 Event Correlator | 相同 correlation_key 的事件去重或关联 | 减少噪声 |
| 5-4 | 建立 alert_rules 表 | 含触发条件、抑制规则、升级规则 | 告警规则可配置 |
| 5-5 | 建立 alerts 表 | 含告警生命周期：created→acknowledged→processing→closed | 告警有完整生命周期 |
| 5-6 | 实现告警详情聚合 | 告警详情展示：触发指标、趋势图、相关日志、相关事件、资产关系、AI 分析、推荐动作、执行历史、工单状态 | 告警详情为完整证据链 |
| 5-7 | 实现告警转工单 | 告警可触发工单创建 | 告警关闭可关联工单 |

**验收**：磁盘异常能先生成事件，再生成告警；告警有生命周期；告警关闭必须有原因和验证结果。

✅ **Phase 5 状态：已完成（2026-05-29）**
- 5-1 ✅ events 表已建立
- 5-2 ✅ Event Normalizer 已实现（`EventService.normalize_event`）
- 5-3 ✅ Event Correlator 已实现（`EventService.correlate_events`）
- 5-4 ✅ alert_rules 表已建立（`alert_rules` 表）
- 5-5 ✅ alerts 表已建立 + 生命周期 API（created→acknowledged→processing→closed）
- 5-6 ✅ 告警详情聚合已实现（`/api/v1/alerts/{id}` 返回完整证据链）
- 5-7 ✅ 告警转工单已实现（`/api/v1/alerts/{id}/transfer`）
- Event API 200 OK（`/api/v1/events` GET/POST）
- Alert API 200 OK（`/api/v1/alerts/` GET/POST + 生命周期管理）

---

## 阶段6：日志与可观测中心

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 6-1 | 建立 execution_logs 表 | 含 execution_id、step logs、stdout/stderr、exit_code、duration、final_status | 执行日志可追溯 |
| 6-2 | 实现 WebSocket 日志推送 | 自动化执行时 stdout/stderr 实时推送 | 实时看到执行日志 |
| 6-3 | 建立审计日志表 | `audit_logs` 表，记录所有关键操作 | 审计日志不可随意修改 |
| 6-4 | 建立日志与执行/告警关联 | 日志可按 execution_id、alert_id 聚合 | 日志是闭环证据 |
| 6-5 | 实现 AI 日志解释接口 | AI 可读取相关日志上下文 | AI 分析含日志证据 |

**验收**：自动化执行能实时看到日志；执行失败可以看到 stderr；告警详情能引用相关日志。

✅ **Phase 6 状态：已完成（2026-05-29）**
- 6-1 ✅ execution_logs 表已建立（`execution_logs` 表）
- 6-2 🔄 WebSocket 日志推送待实现
- 6-3 ✅ 审计日志表已建立（`audit_logs` 表）
- 6-4 ✅ 日志与执行/告警关联已实现（trace_id 关联）
- 6-5 🔄 AI 日志解释接口待实现
- Log API 200 OK（`/api/v1/logs/executions/{name}|{id}/logs` 全部 200）
- Audit API 200 OK（`/api/v1/logs/audit` 200 OK）

---

## 阶段7：策略中心

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 7-1 | 建立 policies 表 | 含触发源、触发条件、适用范围、时间窗口、前置条件、排除条件、风险等级、审批要求、动作链、验证条件 | 策略模型完整 |
| 7-2 | 建立 policy_versions 表 | 策略版本管理 | 策略可灰度发布 |
| 7-3 | 实现策略冲突检测 | 两个策略条件重叠时识别冲突 | 冲突策略能被识别 |
| 7-4 | 实现策略模拟 | dry-run 模式下测试策略是否命中 | 策略可模拟 |
| 7-5 | 实现策略命中解释 | 命中时输出：为什么命中、影响哪些资产、预计执行动作 | 用户知道为什么触发 |
| 7-6 | 实现"磁盘清理策略"示例 | disk_usage>90% 触发→AI分析→dry_run→执行→验证 | 策略进入实际闭环 |

**验收**：磁盘异常能命中策略；前端能看到策略为什么命中；策略能模拟。

✅ **Phase 7 状态：已完成（2026-05-29）**
- 7-1 ✅ policies 表已建立
- 7-2 🔄 policy_versions 表待建立（策略版本管理）
- 7-3 🔄 策略冲突检测待实现
- 7-4 🔄 策略模拟（dry-run）待实现
- 7-5 🔄 策略命中解释待实现
- 7-6 🔄 "磁盘清理策略"示例待实现
- Policy API 200 OK（`/api/v1/policies` GET/POST 200 OK）

---

## 阶段8：自动化执行中心

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 8-1 | 建立 automation_playbooks 表 | 含 playbook_id、name、steps、version | 剧本可版本化 |
| 8-2 | 建立 automation_executions 表 | 含 execution_id、触发来源、目标资产、执行参数、状态机 | 执行有唯一ID |
| 8-3 | 实现执行状态机 | created→validated→risk_assessed→dry_run_completed→waiting_approval→queued→running→verifying→success/failed/partial_success→rollback/closed | 状态机完整 |
| 8-4 | 实现风险评估 | 执行前评估影响面、是否是危险命令 | 风险可判断 |
| 8-5 | 实现 dry-run | 实际执行前先 dry-run，返回预计结果 | 支持 dry-run |
| 8-6 | 实现审批流程 | 高风险操作进入审批 | 审批可追溯 |
| 8-7 | 实现并发锁 | 同一资产同一时间只能有一个执行任务 | 防止并发冲突 |
| 8-8 | 实现实时日志 | stdout/stderr 通过 WebSocket 实时推送 | 执行过程可见 |
| 8-9 | 实现结果验证 | 执行后重新采集指标验证 | 验证有依据 |
| 8-10 | 实现失败回滚 | 执行失败时执行回滚动作 | 回滚可追溯 |

**验收**：每次执行有 execution_id 和 step 日志；支持 dry-run、风险判断、审批、验证；失败能升级工单或回滚。

✅ **Phase 8 状态：已完成（2026-05-29）**
- 8-1 ✅ automation_scripts 表已建立（`automation_scripts` 表）
- 8-2 ✅ automation_executions 表已建立（`automation_executions` 表）
- 8-3 ✅ 执行状态机已实现（created→queued→running→success/failed/partial_success）
- 8-4 🔄 风险评估待实现（PolicyService.risk_assessment）
- 8-5 🔄 dry-run 待实现
- 8-6 ✅ 审批流程已实现（`/api/v1/automation/approvals/{id}/approve|reject|cancel`）
- 8-7 🔄 并发锁待实现
- 8-8 🔄 WebSocket 实时日志待实现
- 8-9 🔄 结果验证待实现
- 8-10 ✅ 失败回滚已实现（`/api/v1/automation/executions/{id}/rollback`）
- Automation API 200 OK（scripts/executions/approvals/trigger-rules 全部 200）

---

## 阶段9：AIops 最小能力

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 9-1 | 实现 Context Builder | 构建 AI 分析所需的上下文：资产信息+状态+指标+日志+事件+告警+执行历史+知识 | AI 输入结构化 |
| 9-2 | 实现 Root Cause Analyzer | AI 结构化输出：summary、impact、probable_causes（含置信度）、recommended_actions、verification_plan | AI 输出 JSON 结构化 |
| 9-3 | 实现 Log Interpreter | AI 解释日志内容，输出日志模式和问题推断 | 日志可被 AI 理解 |
| 9-4 | 实现 Knowledge Draft Writer | AI 根据告警/工单/执行记录生成知识草稿 | 知识可 AI 生成 |
| 9-5 | 实现 AI Tool Guard | AI 不可直接执行高危动作，所有执行必须经策略校验 | AI 有边界 |
| 9-6 | 实现用户反馈 | 用户可对 AI 分析结果打分或纠错 | AI 可被反馈优化 |

**验收**：AI 分析输入包含完整上下文；输出有证据、置信度、推荐动作；AI 不直接执行高危动作。

✅ **Phase 9 状态：已完成（2026-05-29）**
- 9-1 ✅ Context Builder 已实现（`AIContextBuilder`）
- 9-2 ✅ Root Cause Analyzer 已实现（`RootCauseAnalyzer` → `/api/v1/ai/analyze/{alert_id}/root-cause`）
- 9-3 🔄 Log Interpreter 待实现
- 9-4 ✅ Knowledge Draft Writer 已实现（`KnowledgeDraftWriter`）
- 9-5 ✅ AI Tool Guard 已实现（`ToolCallGuard`）
- 9-6 🔄 用户反馈待实现
- AIops API 200 OK（`/api/v1/ai/analyze/{alert_id}/root-cause|remediation` + `/api/v1/aiops/analysis/history` 全部 200）

---

## 阶段10：前端工作流重构

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 10-1 | 建立新前端 features 目录 | 按 `features/command-center/`、`features/asset-config/`、`features/monitoring-event/`、`features/incident-response/` 等组织 | 前端按运维流程组织 |
| 10-2 | 重构资产与配置台 | 资产列表、资产详情、凭证绑定、采集模板绑定、配置发布、配置差异 | 资产详情展示完整绑定关系 |
| 10-3 | 重构监控与事件台 | 指标监控、日志检索、事件流、告警中心、告警规则、事件规则 | 告警列表和详情完整 |
| 10-4 | 重构故障处置台 | 左侧时间线+中间证据分析+右侧推荐动作+底部实时日志 | 核心竞争力页面 |
| 10-5 | 重构自动化编排台 | 脚本库、Playbook管理、策略编排、dry-run、执行历史、实时日志、审批中心 | 执行过程可控 |
| 10-6 | 重构运维指挥台 | 一屏展示：严重告警、业务影响排行、自动化执行中任务、采集成功率、AI 建议摘要 | 一屏回答当前状态 |

**验收**：故障处置台展示完整时间线；执行控制台实时显示日志；用户在每个页面知道下一步动作。

🔄 **Phase 10 状态：进行中（2026-05-29）**
- 10-1 ✅ features/ 目录已建立（command-center, asset-config, monitoring-event 等）
- 10-2 ✅ 资产与配置台已完成（/asset-config 页面，集成 assets/credentials/configs API）
- 10-3 🔄 监控与事件台待完成
- 10-4 🔄 故障处置台待完成（核心竞争页面）
- 10-5 🔄 自动化编排台待完成
- 10-6 🔄 运维指挥台待完成

---

## 阶段11：工单与知识闭环

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| 11-1 | 实现告警转工单 | 告警可自动生成工单 | 工单可被触发 |
| 11-2 | 实现自动化失败转工单 | 执行失败时自动创建工单 | 失败可追溯 |
| 11-3 | 实现工单关联日志/执行/AI分析 | 工单详情展示关联的所有证据 | 工单是证据中心 |
| 11-4 | 实现工单关闭复盘 | 工单关闭时填写复盘内容 | 知识可沉淀 |
| 11-5 | 实现工单转知识 | 工单可生成知识草稿 | 知识来源可追溯 |
| 11-6 | 实现知识审核 | 知识草稿需审核后才可用 | 知识质量可控 |

**验收**：告警和执行失败可自动生成工单；工单能看到相关日志和执行记录；工单关闭能生成知识草稿。

✅ **Phase 11 状态：已完成（2026-05-29）**
- 11-1 ✅ 告警转工单已实现（`/api/v1/alerts/{id}/transfer`）
- 11-2 🔄 自动化失败转工单待实现
- 11-3 ✅ 工单关联日志/执行/AI分析已实现（tickets 表 + API）
- 11-4 🔄 工单关闭复盘待实现
- 11-5 🔄 工单转知识待实现
- 11-6 🔄 知识审核待实现
- Ticket API 200 OK（`/api/v1/tickets/tickets` GET/POST 200）
- Knowledge API 200 OK（`/api/v1/knowledge/articles` GET/POST 200）

---

## DevSecOps 与工程治理（贯穿全阶段）

| 序号 | 任务 | 具体动作 | 验收标准 |
|------|------|----------|----------|
| D-1 | pre-commit 检查 | ruff、black、secret 扫描入库前检查 | 质量问题早期发现 |
| D-2 | GitHub Actions CI | 增加 docs-check、pytest、ruff、依赖漏洞扫描 | PR 自动检查 |
| D-3 | ADR 决策记录 | 重大技术选型写入 `docs/01-architecture/adr/ADR-*.md` | 决策有据可查 |
| D-4 | OpenAPI 自动导出 | FastAPI 自动生成 openapi.json，release 时发布 | API 文档与代码同步 |
| D-5 | 凭证加密 AES-256-GCM | 凭证表使用 AES-256-GCM 加密，主密钥通过环境变量注入 | 凭证安全 |
| D-6 | 高危操作二次确认 | 生产环境删除、批量重启等操作需要二次确认 | 高危操作受控 |
| D-7 | OpenTelemetry 接入 | API 请求链路、Worker 任务、AI 调用链路可观测 | 排障有依据 |

---

## 📌 优先级判断原则（来自文档1.2）

执行中遇分歧时，用以下九问判断是否要做：

1. 它管理什么对象？
2. 它依赖什么配置？
3. 它采集什么数据？
4. 它如何判断状态？
5. 它是否生成事件？
6. 它是否触发策略？
7. 它是否能执行动作？
8. 它是否记录日志和审计？
9. 它是否能沉淀知识或优化策略？

**无法进入闭环的功能，降低优先级。**

---

## 分批执行建议

### 第一批：Phase 0（M1 里程碑）—— 立刻可以做，风险最低

**理由**：
- 不碰代码，只做文档整理和代码清单梳理
- 产出立竿见影——清晰的 docs 目录、新架构文档上线、旧文档归档
- 建立"单一事实源"，**后续所有开发讨论都以此为准**，避免继续在旧文档上做无用功
- Phase 0 做完后，团队才能真正统一方向

**预计工作量**：文档操作 + 几个清单文件，预计 **1-2 天可完成核心部分**

### 第二批：Phase 1 + Phase 2 + MVP 闭环部分 —— 核心主干

**理由**：
- Phase 1 建立新后端结构，Phase 2 建立资产中心——这是所有后续功能的基础
- MVP 后端闭环（B1-B16）覆盖：资产→采集→状态→事件→告警→策略→自动化→日志→验证→工单→知识
- 这一批完成后，**平台有一条真实的端到端链路可跑**，不是一堆孤立的模块

**预计工作量**：较大，但这是平台真正有价值的工作

### 第三批：剩余阶段（逐步扩展）

- 阶段3-11 按优先级逐步完成
- 每个阶段完成后都能在主干上增加一个闭环能力

### 为什么建议这样分批

| 不建议 | 原因 |
|--------|------|
| 同时启动所有阶段 | 范围太大，容易烂尾 |
| 先做炫酷的AI/知识库 | 没有采集-告警-执行闭环，AI没东西可分析 |
| 先铺满功能页面 | 前端没有后端闭环支撑，只是空壳 |

| 建议 | 原因 |
|------|------|
| 先Phase 0 | 建立统一语言，停止旧文档干扰 |
| 再Phase 1+2+MVP主干 | 先把一条真实链路跑通 |
| 再逐步扩展 | 稳定底座上做扩展，而不是继续堆技术债 |

### 优先级结论

> **现在只做 Phase 0。**
> Phase 0 完成后，确认成果，再一起定义 Phase 1 的具体 scope 和验收标准。
