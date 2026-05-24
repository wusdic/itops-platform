# ITOps Platform 重构设计文档

> 基于《ITOps 后台代码遍历检查与改进报告》和《ITOps 平台定位与完整架构功能设计报告》
> 编制日期：2026-05-23（v2.0）
> 项目路径：/home/zcxx/.hermes/projects/itops_platform/

---

## 一、现状评估

### 1.1 代码规模

| 维度 | 数值 |
|------|------|
| Python 文件数 | 316 个 |
| 总代码量 | ~4.6 MB |
| API 路由文件 | 20 个（api/routes/） |
| 核心业务模块 | 5 个（modules/business/） |
| 采集器模块 | 10+ 个（modules/collection/） |

### 1.2 已有模块覆盖

```
认证 Auth       ✓ 基础完整（需强化安全）
资产 Assets     ✓ 基础完整（缺CMDB关系）
发现 Discovery  ✓ 已修复持久化（本次）
采集 Collection ✓ 亮点模块，能力丰富
监控 Monitoring △ 基础指标，缺趋势/统计/降噪
告警 Alerts     △ 接口存在，缺聚合/关联/抑制
工单 Workorder  △ 基础CRUD，缺状态机/评论/附件
知识 Knowledge  △ 后端存在，缺闭环/审核/RAG
AI              △ 接口多，缺上下文/工具调用/降级
自动化 Automation ✗ 严重缺陷：脚本/任务/执行混用，无持久化
通知 Notification △ 渠道完整，缺消息中心/推送/升级策略
系统 Admin      △ 基础完整，缺菜单/字典/权限保存
备份 Backup     ？ 需复核是否存在
```

### 1.3 P0 问题清单（必须优先修复）

| 编号 | 问题 | 根因 |
|------|------|------|
| GAP-01 | 自动化模块脚本/任务/执行混用，无持久化 | 概念模型错误，无 AI 决策能力 |
| GAP-02 | 前后端 API 路径不一致 | 路由 prefix 混乱 |
| GAP-06 | 系统管理菜单/字典静态化 | 无数据库表和 CRUD |
| GAP-08 | 备份模块版本不一致 | 需复核实际状态 |
| GAP-04 | 工单缺状态机/评论/附件 | 数据模型缺失 |

---

## 二、重构目标

### 2.1 产品定位

**面向中小政企 IT 团队的轻量级 AI 原生 ITOps/AIOps 平台**

### 2.2 三条核心闭环（必须可演示、可交付、可验证）

```
闭环1：资产发现与纳管
  发现任务 → IP/SNMP扫描 → 设备导入 → 绑定业务系统 → 资产统计

闭环2：监控告警到工单
  指标采集 → 触发告警 → 确认/升级 → 转工单 → SLA → 关闭 → 复盘

闭环3：AI辅助排障
  告警/工单 → 无可用脚本？→ 本地LLM分析 → 接管处理 → 沉淀为脚本
            → 有可用脚本 → 执行脚本 → 成功 → 推送案例到知识库
```

### 2.3 重构原则

1. **不破坏已验证功能**：认证、采集、基础 API 在重构前必须保持可用
2. **先设计后实施**：每个模块的设计必须先输出详细方案再动手
3. **数据模型先行**：新增/修改功能前先确定数据模型，再改 API
4. **前后端路径一致**：同一对象的前后端路径必须完全对应
5. **可逆性**：每次改动必须可回滚，不破坏现有数据
6. **模块边界清晰**：功能归属以"高内聚低耦合"为原则，避免模块间循环依赖

---

## 三、总体架构

### 3.1 分层结构

```
┌─────────────────────────────────────────────────┐
│              前端门户层 (Vue 3 + Naive UI)        │
│  工作台 | 资产视图 | 监控大屏 | 告警中心 | 工单中心 │
│  AI助手 | 自动化中心 | 报表中心 | 系统管理         │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────────┐
│              API 网关层 (FastAPI)                │
│  统一鉴权 | 限流 | 日志 | 错误处理 | OpenAPI     │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              业务服务层 (routes/)                │
│  auth | admin | asset | monitoring | workorder │
│  knowledge | ai | notification | automation     │
│  discovery | inspection | report | backup      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              业务逻辑层 (modules/business/)       │
│  asset_management | knowledge_base | ai_copilot │
│  dashboard | monitoring | notification          │
│  workorder | backup_manager | device_importer   │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              运维能力层 (modules/collection/)    │
│  SNMP/SSH/IPMI/HTTP/WMI/Redfish/VMware 采集器   │
│  采集器工厂 | 适配器注册 | 设备管理 | 指纹识别    │
│  modules/automation/: 脚本执行 | 任务调度 | 自愈  │
└─────────────────────────────────────────────────┘
                   │
┌─────────────────────────────────────────────────┐
│              数据存储层                          │
│  MySQL (业务) | Redis (缓存/队列)                 │
│  TDengine/InfluxDB (时序) | Qdrant (向量)        │
│  MinIO (对象存储)                                │
└─────────────────────────────────────────────────┘
```

### 3.2 模块边界决策（全局）

在多模块重构过程中，发现以下功能归属需要明确：

| 功能 | 原归属 | 正确归属 | 理由 |
|------|--------|---------|------|
| SOP 生成 | 自动化模块 | **知识库模块** | SOP 本质是知识文档，审核/分类/版本都应该在知识库 |
| 脚本推荐 | 自动化模块 | **知识库模块** | 推荐本质是"历史经验"，知识库天然适合 |
| 通知模板 | 自动化/通知 | **通知模块** | 模板和渠道紧耦合 |
| 升级策略 | 自动化/通知 | **通知模块** | 值班表、升级规则属于通知能力 |
| 定时调度 | 各模块各自实现 | **scheduler 模块（新增）** | 统一调度服务，各模块调用 |
| 告警聚合 | monitoring 模块 | **monitoring 模块** | 与指标采集紧耦合 |
| 告警转工单 | monitoring 模块 | **monitoring 模块** | 触发规则在 monitoring 层 |

---

## 四、模块级重构方案

### 4.1 自动化模块（GAP-01，P0）

**详细设计文档**：`docs/REFACTORING_AUTOMATION.md`

**核心设计目的**：
```
事件/告警/工单  →  无直接可用脚本？
                      ↓
              本地大模型自动分析  →  接管处理
                      ↓
              成功解决 → 沉淀为可复用脚本
                      ↓
              后期可单独调用或自由组合
```

**模块架构**：
```
┌──────────────────────────────────────────────────────┐
│              事件入口层（Event Intake）               │
│  告警触发 | 工单触发 | 手动触发 | 定时触发            │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│           AI 决策引擎（AI Decision Engine）            │
│  LLM 分析 → 有脚本？执行脚本                         │
│          → 无脚本？LLM 生成临时脚本 → 执行            │
│          → 复杂？转工单/人工                         │
│          → 成功后 → 沉淀为正式脚本                    │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│            执行层（Execution Layer）                  │
│  脚本库（Scripts）| 任务调度（Tasks）| 回滚          │
└──────────────────────────────────────────────────────┘
```

**关键能力**：
- AI 决策引擎：调用本地 LLM（ai_copilot），决策路由
- 脚本资产化：手动创建 + AI 自动生成（标记来源）
- 经验沉淀：执行成功 → 推送案例到知识库

**模块间接口**：
- 自动化 → 知识库：`POST /api/v1/knowledge/fault-case/from-automation`（推送案例）
- 自动化 → 知识库：`GET /api/v1/knowledge/fault-case/recommend-scripts`（查询推荐脚本）
- 自动化 → 通知：`POST /api/v1/notification/send`（升级通知）
- 监控/工单 → 自动化：`POST /api/v1/automation/events`（触发事件）

**数据库模型**：automation_scripts, automation_tasks, automation_executions, automation_execution_logs, automation_trigger_rules, automation_ai_decisions, automation_script_versions

**文件清单**：
- 新增：`scripts/migration/011_automation_module.sql`
- 新增：`modules/foundation/db_models/automation.py`
- 新增：`modules/business/automation/event_handler.py`
- 新增：`modules/business/automation/decision_engine.py`
- 新增：`modules/business/automation/script_manager.py`
- 新增：`modules/business/automation/execution_tracker.py`
- 修改：`api/routes/automation.py`
- 修改：前端 4 个 vue 文件

---

### 4.2 系统管理模块（GAP-06，P0）

**现状**：菜单静态、字典项仅示例、权限保存不调用 API。

**新增数据模型**：

```
admin_menus        菜单表（id, parent_id, name, path, component, permission_code, sort, visible）
admin_dict_types   字典类型（type_code, type_name）
admin_dict_items   字典项（type_code, item_label, item_value, sort, status）
admin_role_permissions 角色权限关联（role_id, permission_code, scope）
```

**新增 API**：
```
GET/POST/PUT/DELETE  /api/v1/admin/menus
GET/POST/PUT/DELETE  /api/v1/admin/dict/types
GET/POST/PUT/DELETE  /api/v1/admin/dict/items
POST                  /api/v1/admin/roles/{id}/permissions   # 权限保存
GET                   /api/v1/admin/roles/{id}/permissions   # 权限查询
```

---

### 4.3 工单模块（GAP-04，P0）

**现状**：基础 CRUD 存在，缺状态机、评论、附件、转派、复盘。

**新增数据模型**：

```
workorder_status_flows   状态流转规则（from_status, to_status, allowed_roles）
workorder_comments       工单评论（workorder_id, user_id, content, attachments）
workorder_attachments     工单附件（workorder_id, user_id, filename, file_path, size）
workorder_transfers      工单转派（workorder_id, from_user, to_user, reason, transferred_at）
workorder_postmortems    工单复盘（workorder_id, root_cause, 5why, corrective_actions）
sla_rules                SLA规则（priority, business_system, response_hours, resolution_hours）
```

**状态机**：
```
draft → new → assigned → processing → pending → solved → closed
                                    ↘ rejected → cancelled
```

**新增 API**：
```
PATCH              /api/v1/workorders/{id}/status       # 状态流转
POST               /api/v1/workorders/{id}/transfer     # 转派
GET/POST           /api/v1/workorders/{id}/comments     # 评论
POST               /api/v1/workorders/{id}/attachments   # 附件
POST               /api/v1/workorders/{id}/close        # 关闭
POST               /api/v1/workorders/{id}/postmortem    # 复盘
GET/POST           /api/v1/admin/sla-rules              # SLA规则
```

---

### 4.4 监控与告警模块（Monitoring，P1）

**现状**：基础指标接口存在，缺历史趋势、统计、TOP N、告警聚合。

**新增数据模型**：

```
alert_correlations   告警关联（group_key, business_id, root_alert_id, alert_ids）
alert_silences       告警静默（alert_rule_id, start_time, end_time, reason）
metric_rollups       指标聚合（device_id, metric_name, time_bucket, avg/max/min）
```

**新增 API**：
```
GET  /api/v1/monitoring/metrics/history           # 指标历史趋势
GET  /api/v1/monitoring/metrics/top/{type}         # TOP N 指标
GET  /api/v1/monitoring/alerts/statistics          # 告警统计
POST /api/v1/monitoring/alerts/{id}/suppress       # 告警抑制
POST /api/v1/monitoring/alerts/{id}/convert-workorder  # 告警转工单
GET  /api/v1/monitoring/alerts/correlations        # 告警关联分析
```

**重要**：告警转工单后，工单模块需要能触发自动化（见 4.1 自动化模块的事件入口）。

---

### 4.5 知识库模块（P1）

**现状**：后端已有 SOP/案例/分类/标签，缺与自动化模块的闭环。

**新增/修改 API**：

```
# 接收自动化推送的故障案例
POST /api/v1/knowledge/fault-case/from-automation  # 自动化成功执行后推送

# 推荐相似历史案例及对应脚本
GET /api/v1/knowledge/fault-case/recommend-scripts  # 自动化 AI 决策时查询

# AI 生成脚本审核通过后转正式
POST /api/v1/knowledge/scripts/from-automation/{script_id}/promote  # AI脚本转正式
```

**知识库负责的功能**：
- SOP 文档的 CRUD、审核流程（自动化模块不生成 SOP，只推送案例）
- 故障案例的 CRUD、分类（可从自动化执行成功后的案例创建）
- RAG 向量检索（自动化模块调用 AI 分析时，提供知识库上下文）

**知识库不负责的功能**：
- 脚本管理（归自动化模块）
- 脚本执行（归自动化模块）
- 告警触发（归监控模块）

---

### 4.6 通知模块（P1）

**现状**：渠道完整，缺消息中心、推送、升级策略、通知模板。

**新增数据模型**：

```
notification_messages       站内消息（user_id, title, content, type, related_object, is_read）
notification_templates      通知模板（channel, event_type, template_content）
duty_rosters               值班表（user_id, shift_start, shift_end, escalation_order）
escalation_policies        升级策略（rule_id, condition, escalation_level, timeout）
```

**新增 API**：
```
GET    /api/v1/notifications/messages                 # 消息列表
GET    /api/v1/notifications/messages/unread-count    # 未读数
POST   /api/v1/notifications/messages/{id}/read       # 标记已读
POST   /api/v1/notifications/messages/read-all        # 全部已读
GET/POST /api/v1/admin/notification-templates         # 模板管理
GET/POST /api/v1/admin/duty-rosters                  # 值班表
GET/POST /api/v1/admin/escalation-policies           # 升级策略
```

**通知模块负责的功能**：
- 通知模板管理（自动化模块调用，不生成模板）
- 值班表和升级策略（告警/自动化模块调用，决定通知谁）
- 站内消息（各模块的通知汇总展示）

**通知模块不负责的功能**：
- 何时发送通知（由自动化/监控等业务模块决定）
- 通知内容生成（由业务模块提供，模板负责渲染）

**实时推送**：通过 WebSocket 或 SSE 推送告警、工单、审批、自动化执行结果。

---

### 4.7 备份模块（GAP-08，P0）

**需复核**：差距报告称 backup.py 不存在，API 审计显示已注册。实际代码已存在（`api/routes/backup.py`）。

**新增数据模型**：

```
backup_jobs            备份任务（id, name, scope, schedule, retention_days, encryption, status）
backup_files           备份文件（job_id, file_path, file_size, checksum, created_at）
restore_tasks          恢复任务（backup_file_id, status, requested_by, approved_by, restored_at）
```

**新增 API**：
```
POST   /api/v1/backups                           # 创建备份
GET    /api/v1/backups                           # 备份列表
GET    /api/v1/backups/{id}                      # 备份详情
GET    /api/v1/backups/{id}/download             # 下载备份
POST   /api/v1/backups/{id}/restore              # 恢复
DELETE /api/v1/backups/{id}                      # 删除备份
GET    /api/v1/backups/policies                  # 备份策略
POST   /api/v1/backups/policies                  # 创建策略
```

---

### 4.8 前端路径修复（GAP-02，P0）

**现状**：前后端 API 路径不一致，导致页面调用失败。

**统一路径规范**（所有模块）：
```
前缀: /api/v1/{module}
路由: /api/v1/{module}/{resource}
      /api/v1/{module}/{resource}/{id}
      /api/v1/{module}/{resource}/{id}/sub-action
```

**需修复的路径映射**（从 frontend 代码审计）：
| 前端调用路径 | 后端实际路径 | 修复目标 |
|---|---|---|
| `/api/v1/admin/logs` | `/api/v1/admin/logs` (× 404) | `/api/v1/admin/log-stats` |
| `/api/v1/discovery/networks` | ✓ 正确 | - |
| `/api/v1/monitoring/alerts` | ✓ 正确 | - |
| `/api/v1/automation/*` | 严重混用 | 拆分 scripts/tasks/executions |

---

## 五、实施计划

### 阶段 0：可运行基线（1-2 周）

**目标**：修复最阻碍演示的 P0 问题，确保核心流程不断。

| 任务 | 工作内容 | 验收标准 |
|------|---------|---------|
| 自动化模块重构 | 创建 scripts/tasks/executions 模型、AI 决策引擎、事件入口 | 脚本创建/执行/AI决策可用 |
| 前端路径修复 | 统一前后端 API 路径 | 核心页面不报 404/503 |
| 系统管理菜单持久化 | 创建 admin_menus 表和 CRUD | 菜单可增删改 |
| 备份模块复核 | 确认 backup.py 实际状态 | 备份/恢复可用 |

### 阶段 1：三条主闭环（3-6 周）

**目标**：让三条核心闭环可演示。

| 闭环 | 任务 | 验收标准 |
|------|------|---------|
| 资产闭环 | 设备发现→导入→分组→统计 | 完整流程不断 |
| 告警工单闭环 | 告警→确认→转工单→SLA→关闭 | 工单状态机可用 |
| AI 排障闭环 | 告警→AI分析→SOP推荐→案例 | AI返回引用来源 |

### 阶段 2：企业交付能力（6-10 周）

**目标**：RBAC、审计、通知、备份恢复、巡检报表。

### 阶段 3：AIOps 增强（10-16 周）

**目标**：告警关联、知识 RAG、自动化 Runbook、异常检测。

---

## 六、重构规范

### 6.1 数据模型规范

```python
# 所有模型必须包含审计字段
class ExampleModel(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    status = Column(String(32), default="active")

    # 审计字段
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(64))
    updated_by = Column(String(64))

    # 索引
    __table_args__ = (
        Index('idx_status', 'status'),
    )
```

### 6.2 API 响应规范

```python
# 统一响应格式
{
    "code": 0,           # 0=成功，非0=错误
    "message": "success",
    "data": {...},       # 实际数据
    "request_id": "..."  # 请求追踪 ID
}

# 分页响应
{
    "code": 0,
    "message": "success",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 20
    }
}
```

### 6.3 分层约束

- **routes 层**：只做 HTTP 处理（请求校验、响应组装），不写业务逻辑
- **business 层**：跨多个模型的操作、复杂业务规则
- **foundation 层**：纯数据操作，不含业务逻辑

### 6.4 安全规范

- 所有敏感操作写 `operation_logs`
- 设备凭据加密存储（Fernet 对称加密）
- 自动化脚本执行前必须参数校验
- 高危操作（删除、恢复）需审批记录

### 6.5 模块边界规范

- 功能归属以"高内聚低耦合"为原则
- 跨模块调用必须通过 API（HTTP）或明确的服务接口，不直接引用其他模块的 DB 模型
- 自动化模块负责"执行"，知识库负责"沉淀"，通知模块负责"告知"

---

## 七、已验证可行的改动（保留）

以下本次会话中已完成的改动，必须保留：

| 文件 | 改动内容 |
|------|---------|
| `api/middleware/logging.py` | 中间件同时写 operation_logs 和 log_groups/log_items |
| `api/routes/auth.py` | InMemoryUserStore → DBUserStore（system_users 表） |
| `modules/foundation/db_models/system.py` | 新增 SystemUser、NetworkScanConfig、DiscoveryTask 模型 |
| `api/routes/discovery.py` | 网段和任务从内存存储改为数据库持久化 |

---

## 八、风险与约束

1. **回滚风险**：重构自动化模块可能破坏现有 automation.py 的调用方
2. **数据迁移**：新增表需要处理和旧数据的兼容
3. **前端配合**：部分重构需要前端同步修改（建议前端单独发起重构任务）
4. **测试覆盖**：当前无集成测试，改动后手动验证成本高
5. **时间约束**：必须在保持现有功能可用的前提下进行
6. **模块依赖**：自动化模块依赖知识库（推送案例），需确保知识库接口可用

---

## 九、模块依赖关系图

```
AI Copilot
    ↑
    │（LLM 调用）
    │
自动化 ──────────────────────────────→ 知识库
    │                                    ↑
    │ 推送案例                           │ 提供案例、推荐脚本
    │                                    │
通知 ──────────────→ 监控              自动化
    ↑                  ↑                  │
    │ 升级通知         │ 告警触发          │
    │                  ↓                  │
    └──────── 工单 ←───┘                  │
              ↑                            │
              └────────────────────────────┘
                       触发事件
```

---

## 十、详细设计文档索引

| 模块 | 详细设计文档 |
|------|------------|
| 自动化 | `docs/REFACTORING_AUTOMATION.md` |
| 系统管理 | 整合到本文档 |
| 工单 | 整合到本文档 |
| 监控 | 整合到本文档 |
| 知识库 | 整合到本文档 |
| 通知 | 整合到本文档 |
| 备份 | 整合到本文档 |

---

*本文档为第二版，新增模块边界决策、自动化 AI 驱动架构、模块间接口设计。随着重构推进，内容将持续更新。*
