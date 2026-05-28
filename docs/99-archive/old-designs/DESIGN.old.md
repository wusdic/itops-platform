> 文档状态：archived
> 替代文档：
>   - 架构总纲：docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md
>   - 开发计划：docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md
> 归档原因：本文件内容已被新架构文档取代，不再作为开发依据。
> 最后归档日期：2026-05-28

---

# ITOps Platform 设计文档

> **版本**: v2.0  
> **更新日期**: 2026-05-28  
> **状态**: 当前主设计文档

---

## 1. 平台概述

### 1.1 定位

ITOps Platform 是**企业级运维管理平台**，面向内部私有化部署场景，覆盖"设备发现→设备纳管→监控告警→工单处理→AI 辅助决策"的完整运维闭环。

### 1.2 核心目标

| 目标 | 描述 | 优先级 |
|------|------|--------|
| 设备全自动化 | IP 段扫描 + SNMP 发现 → 自动识别类型 → 一键导入 | P0 |
| 智能监控告警 | 指标采集 → 阈值告警 → 自动收敛 → 告警升级 | P0 |
| 工单闭环 | 告警自动转工单 → SLA 计时 → 多级审批 → 案例沉淀 | P0 |
| AI 辅助决策 | 本地 LLM（Qwen3.5-0.8B）→ 告警分析 → 处置建议 | P1 |
| 自动化运维 | 定时任务 → 脚本执行 → 自动巡检 → 报告生成 | P1 |

### 1.3 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Axios | 单页应用 |
| 后端 | Python 3.10+ / FastAPI + SQLAlchemy | 异步 API 框架 |
| 数据库 | MySQL 8.0 | 主数据存储 |
| 缓存 | Redis | 会话、限流、队列 |
| 时序库 | TDengine | 监控指标存储（预留） |
| 对象存储 | MinIO | 文件、日志、备份 |
| AI | Qwen3.5-0.8B（llama.cpp） | 本地 LLM，端口 11436 |

### 1.4 用户规模

- **小型**: 1-50 台设备，单机部署
- **中型**: 50-200 台设备，单机部署 + Redis
- **大型**: 200+ 台设备，分片 + 多节点

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层 (Web)                          │
│                   Vue 3 + Element Plus + Axios                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API 网关层 (FastAPI)                       │
│                   JWT / API Key 认证 + RBAC                     │
│  /api/v1/auth  /api/v1/assets  /api/v1/monitoring  /api/v1/... │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   业务模块层     │ │   采集模块层     │ │   基础模块层     │
│ modules/business │ │ modules/collection│ │ modules/foundation│
│                 │ │                 │ │                 │
│ · monitoring     │ │ · discovery     │ │ · db_models     │
│ · workorder      │ │ · snmp_collector│ │ · auth_manager  │
│ · knowledge_base  │ │ · ssh_collector │ │ · sharding      │
│ · ai_copilot     │ │ · api_collector │ │                 │
│ · report_generator│ │ · device_manager │ │                 │
│ · automation     │ │                 │ │                 │
│ · notification   │ │                 │ │                 │
│ · asset_management│ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         数据存储层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  MySQL   │  │  Redis   │  │  MinIO   │  │ TDengine │      │
│  │ :3306    │  │  :6379   │  │ :9000    │  │  :6030   │      │
│  │ 主数据    │  │缓存/会话│  │ 文件存储  │  │时序指标  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         目标设备层                               │
│  Linux / Windows 服务器、网络设备（交换机/路由器）、安全设备     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块依赖关系

```
modules/foundation/
├── db_models/          ← 所有 ORM 模型（设备、工单、告警、知识库等）
├── auth_manager/       ← JWT、RBAC、LDAP
└── sharding.py         ← 分片路由（alerts/work_orders）

modules/collection/
├── discovery/           ← IP 扫描、SNMP 发现、指纹识别
├── snmp_collector/      ← SNMP 采集
├── ssh_collector/      ← SSH/CLI 采集
├── api_collector/      ← REST API 采集（Zabbix/Prometheus/华为 IMC）
├── device_manager.py   ← 采集调度器
└── collector_factory.py← 采集器工厂

modules/business/
├── monitoring/         ← 告警引擎、规则、仪表盘
├── workorder/          ← 工单 CRUD、审批流、SLA
├── knowledge_base/      ← 文档、案例、SOP、RAG 检索
├── ai_copilot/         ← LLM 对话、根因分析、处置建议
├── report_generator/    ← 巡检报告、统计报表
├── automation/          ← 定时任务、脚本执行、回滚
├── notification/       ← 通知服务（站内/邮件）
├── asset_management/   ← 资产管理
└── dashboard/          ← 仪表盘布局持久化

api/routes/
├── auth.py             ← 登录/登出/JWT
├── device_api.py       ← 设备 CRUD（主要设备接口）
├── asset.py            ← 资产接口（与 device_api 部分重复）
├── discovery.py        ← 网络发现 API
├── monitoring.py       ← 监控/告警 API
├── workorder.py        ← 工单 API
├── knowledge.py        ← 知识库 API
├── ai.py               ← AI 对话/分析 API
├── notification.py     ← 通知 API
├── automation.py       ← 自动化任务 API
├── report.py           ← 报表 API
├── system.py           ← 系统管理（菜单/字典/用户/角色）
├── admin.py            ← 管理员 API（API Keys、适配器）
├── device_metrics.py   ← 设备指标 API
├── device_import.py    ← 批量导入 API
├── backup.py           ← 备份恢复 API
├── inspection.py       ← 巡检报告 API
├── log_service.py      ← 日志查询 API
├── tenant.py           ← 租户 API
├── api_keys.py         ← API Key 管理
├── watermark.py        ← 水印 API
├── sharding.py         ← 分片路由测试
├── deploy.py           ← 部署管理 API
├── vendor_credentials.py← 厂商凭证 API
└── notification.py     ← 通知 API
```

---

## 3. 核心业务流程

### 3.1 设备全生命周期

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  发现    │───▶│  录入    │───▶│  纳管    │───▶│  监控    │───▶│  告警    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
 IP段/SNMP      批量导入       采集配置         指标入库         阈值触发
 ARP扫描        手动录入       采集项开关       趋势展示         自动收敛
 指纹识别       Excel导入      定时采集        历史数据         告警升级
```

### 3.2 告警 → 工单闭环

```
告警触发 ──▶ 告警确认 ──▶ 自动转工单 ──▶ SLA计时 ──▶ 处理 ──▶ 审批 ──▶ 关闭
    │                                                              │
    └──────────────────▶ AI根因分析 ◀───────────────────────────────┘
                             │
                             ▼
                      处置建议 + 案例沉淀
```

### 3.3 自动化运维

```
定时任务 ──▶ 脚本执行 ──▶ 巡检采集 ──▶ 报告生成 ──▶ 自动归档
                  │
                  ├── 成功 ──▶ 记录执行日志
                  ├── 失败 ──▶ 自动回滚 + 告警通知
                  └── 超时 ──▶ 强制终止 + 标记失败
```

---

## 4. 功能模块详解

### 4.1 配置管理 (CFG)

| 功能 | 文件 | 状态 |
|------|------|------|
| 设备基础信息（IP/类型/厂商/型号） | `db_models/device.py` | ✅ |
| 设备标签和分组 | `db_models/device.py` | ✅ |
| 设备责任人配置 | `db_models/device.py` | ✅ |
| 设备关联业务系统 | `db_models/device.py` | ✅ |
| 采集模板（SNMP/SSH） | `config/templates/*.yaml` | ✅ |
| 采集项精细化开关 | `device_manager.py` | ⚠️ 部分 |
| 阈值告警规则 | `monitoring/rules.py` | ✅ |
| 告警级别/升级/抑制 | `monitoring/alerter.py` | ✅ |
| 通知方式/对象配置 | `notification/` | ✅ |
| 工单自动派单/审批/SLA | `workorder/` | ✅ |
| 定时任务 Crontab | `automation/` | ✅ |

**缺口**: CFG-005（设备配置项版本管理）、CFG-014（采集模板导入导出）、CFG-021（趋势告警）、CFG-026（通知对象按类型/级别/设备精准通知）、CFG-027（聚合告警）

### 4.2 数据采集 (COL)

| 功能 | 文件 | 状态 |
|------|------|------|
| IP 段扫描发现设备 | `discovery/scanner.py` | ✅ |
| SNMP 扫描发现网络设备 | `discovery/snmp_scanner.py` | ✅ |
| ARP 扫描存活主机 | `discovery/arp_scanner.py` | ✅ |
| 设备指纹识别 | `discovery/fingerprinter.py` | ✅ |
| SNMP 采集（系统/接口/资产） | `snmp_collector/` | ✅ |
| SSH 采集（Linux/Windows） | `ssh_collector/` | ✅ |
| REST API 采集（Zabbix/Prometheus/华为 IMC） | `api_collector/` | ⚠️ 部分 |
| WMI/WinRM 采集 Windows | — | ❌ 未实现 |
| 日志文件采集 | `log_collector/` | ⚠️ 部分 |
| 采集结果自动解析入库 | `device_manager.py` | ✅ |
| 采集失败重试 + 告警 | `device_manager.py` | ✅ |
| 预置设备指纹库（21个厂商） | `config/adapters.yaml` | ✅ |

**缺口**: COL-007（增量发现定时检测）、COL-013（Windows WMI 采集）、COL-021（自定义指纹模板）

### 4.3 监控告警 (MON)

| 功能 | 文件 | 状态 |
|------|------|------|
| CPU/内存/磁盘/网络监控 | `monitoring/monitor.py` | ✅ |
| 端口/服务/进程监控 | `monitoring/monitor.py` | ✅ |
| 自定义指标监控 | `monitoring/monitor.py` | ✅ |
| 指标历史数据存储查询 | `storage/tdengine/` | ⚠️ 预留 |
| 告警实时触发 | `monitoring/alerter.py` | ✅ |
| 告警自动收敛（去重/聚合/抑制） | `monitoring/alerter.py` | ✅ |
| 告警自动生成工单 | `monitoring/alerter.py` | ✅ |
| 告警确认/处理/关闭 | `monitoring/` | ✅ |
| 告警升级（超时未处理） | `monitoring/alerter.py` | ✅ |
| 告警屏蔽（维护时段） | `monitoring/` | ✅ |
| 告警统计分析 | `monitoring/` | ✅ |
| 告警审计日志 | `monitoring/` | ⚠️ 部分 |
| 全局态势仪表盘 | `dashboard/` | ✅ |
| 自定义仪表盘布局 | `dashboard/persistence.py` | ✅ |
| 指标历史/TopN 查询 | `monitoring.py` (API) | ✅ |

**缺口**: MON-021（趋势告警）、MON-028（完整审计）、MON-031（按设备分组仪表盘）、MON-033（图表数据导出）

### 4.4 工单管理 (WKO)

| 功能 | 文件 | 状态 |
|------|------|------|
| 工单创建（手动/自动） | `workorder/workorder.py` | ✅ |
| 工单自动派发（基于规则） | `workorder/flow.py` | ✅ |
| 工单状态流转 | `workorder/flow.py` | ✅ |
| 工单转派和升级 | `workorder/flow.py` | ✅ |
| 工单处理记录（时间线） | `workorder/workorder.py` | ✅ |
| 工单附件上传 | `routes/workorder.py` | ✅ |
| 工单关闭和归档 | `workorder/workorder.py` | ✅ |
| 工单草稿保存 | `routes/workorder.py` | ✅ |
| 多级审批流程 | `workorder/approval.py` | ✅ |
| 会签/或签审批 | `workorder/approval.py` | ✅ |
| SLA 时限配置和计时 | `workorder/sla_manager.py` | ✅ |
| SLA 超时自动升级 | `workorder/sla_manager.py` | ✅ |
| SLA 达成率统计 | — | ❌ 未实现 |
| 工单数量/时效/工作量统计 | `report_generator/` | ✅ |
| 工单 Excel 导出 | `report_generator/excel_exporter.py` | ✅ |
| 告警转工单 | `routes/workorder.py` | ✅ |

**缺口**: WKO-023（SLA 达成率统计）

### 4.5 知识库 (KNO)

| 功能 | 文件 | 状态 |
|------|------|------|
| SOP 文档创建/编辑/版本管理 | `knowledge_base/document.py` | ✅ |
| 文档分类/标签/审核发布 | `knowledge_base/` | ✅ |
| 文档全文搜索 | `knowledge_base/search.py` | ✅ |
| 故障案例创建（从工单生成） | `knowledge_base/case.py` | ✅ |
| 案例关联知识文档 | `knowledge_base/case.py` | ✅ |
| 案例 AI 推荐复用 | `ai_copilot/scenarios.py` | ⚠️ 预留 |
| 向量语义检索（RAG） | `knowledge_base/rag.py` | ⚠️ 预留 |
| 知识图谱关联检索 | — | ❌ 未实现 |

### 4.6 AI 助手 (AI)

| 功能 | 文件 | 状态 |
|------|------|------|
| 自然语言对话（本地 LLM） | `routes/ai.py` + `llm_client.py` | ✅ |
| 对话上下文/历史记录 | `routes/ai.py` | ✅ |
| 告警根因分析 | `ai_copilot/root_cause.py` | ✅ |
| 告警处置建议 | `ai_copilot/remediation.py` | ✅ |
| 知识库 RAG 问答 | `knowledge_base/rag.py` | ✅ |
| 统一分析入口 `/ai/analyze` | `routes/ai.py` | ✅ |
| 本地 LLM 接口（Qwen3.5-0.8B） | `llm_client.py` | ✅ |

**AI 服务地址**: `http://localhost:11436`（llama.cpp 服务）

### 4.7 自动化运维 (AUTO)

| 功能 | 文件 | 状态 |
|------|------|------|
| 定时任务 CRUD | `automation/` | ✅ |
| Crontab 表达式解析 | `automation/` | ✅ |
| 一次性/周期任务 | `automation/` | ✅ |
| 任务执行（脚本/命令） | `automation/script_executor/` | ✅ |
| 任务失败自动回滚 | `automation/script_executor/rollback.py` | ✅ |
| 任务执行超时配置 | `automation/` | ✅ |
| 任务失败重试策略 | `automation/` | ✅ |
| 巡检报告自动生成 | `report_generator/inspection_report.py` | ✅ |
| 自动化触发规则（告警触发执行） | `automation/trigger.py` | ✅ |

### 4.8 备份恢复 (BACKUP)

| 功能 | 文件 | 状态 |
|------|------|------|
| 手动备份（数据库+配置文件） | `routes/backup.py` | ✅ |
| 自动定时备份 | `routes/backup.py` | ✅ |
| 备份列表查询 | `routes/backup.py` | ✅ |
| 备份下载 | `routes/backup.py` | ✅ |
| 备份恢复 | `routes/backup.py` | ✅ |
| MinIO 对象存储 | `modules/storage/minio/` | ✅ |

---

## 5. 数据库设计

### 5.1 核心表

| 表名 | 说明 | 分片 |
|------|------|------|
| `devices` | 设备主数据 | 否 |
| `alerts` | 告警记录 | 是（月度/租户） |
| `work_orders` | 工单 | 是（月度/租户） |
| `notification_messages` | 通知消息 | 否 |
| `notification_targets` | 通知对象 | 否 |
| `automation_tasks` | 定时任务 | 否 |
| `automation_scripts` | 脚本库 | 否 |
| `automation_executions` | 执行记录 | 否 |
| `knowledge_documents` | 知识文档 | 否 |
| `knowledge_cases` | 故障案例 | 否 |
| `ai_conversations` | AI 对话 | 否 |
| `ai_messages` | AI 消息记录 | 否 |
| `performance_metrics` | 性能指标 | 是（按设备） |
| `operation_logs` | 操作日志 | 否 |
| `system_backups` | 备份记录 | 否 |

### 5.2 分片策略

```python
# modules/foundation/sharding.py
class MonthlyShard:
    """按月分片：alerts、work_orders"""

class TenantShard:
    """按租户分片：多租户隔离"""

class DeviceShard:
    """按设备分片：performance_metrics"""
```

---

## 6. API 设计

### 6.1 路由前缀规范

```
/api/v1/auth/           认证
/api/v1/users/           用户管理
/api/v1/assets/          资产管理
/api/v1/devices/        设备管理
/api/v1/discovery/       网络发现
/api/v1/monitoring/      监控告警
/api/v1/notifications/  通知
/api/v1/workorders/      工单
/api/v1/ai/              AI 能力
/api/v1/automation/      自动化
/api/v1/reports/         报表
/api/v1/inspection/      巡检
/api/v1/knowledge/       知识库
/api/v1/admin/           系统管理
/api/v1/system/          系统设置
/api/v1/backups/         备份恢复
```

### 6.2 响应格式

```json
// 成功
{"code": 0, "message": "success", "data": {...}}

// 失败
{"code": 非0, "message": "错误描述", "data": null}
```

### 6.3 认证方式

- **JWT**: 登录获取，有效期 24h
- **API Key**: 用于外部系统集成，`/api/v1/admin/api-keys` 管理

---

## 7. 前端页面结构

```
frontend/src/views/
├── login/               登录页
├── layout/               布局容器（侧边栏 + 主内容区）
│   ├── dashboard/        仪表盘
│   ├── system/           系统管理
│   │   ├── adapters.vue  适配器管理
│   │   ├── config.vue    参数配置
│   │   ├── dict.vue      字典管理
│   │   ├── logs.vue      日志查询
│   │   ├── menu.vue      菜单管理
│   │   ├── role.vue      角色管理
│   │   └── user.vue      用户管理
│   ├── monitoring/       监控告警
│   │   ├── alerts.vue    告警列表
│   │   ├── devices.vue   设备监控
│   │   ├── performance.vue 性能监控
│   │   ├── dashboard.vue 监控仪表盘
│   │   ├── triggers.vue   告警规则
│   │   └── maintenance.vue 维护时段
│   ├── discovery/         网络发现
│   │   ├── scan.vue       扫描配置
│   │   └── targets.vue    发现目标
│   ├── workorder/         工单管理
│   ├── knowledge/         知识库
│   ├── ai/                AI 助手
│   ├── automation/        自动化
│   ├── report/           报表
│   ├── inspection/        巡检
│   ├── notification/       消息中心
│   ├── tenants/           租户管理
│   ├── backup/           备份管理
│   ├── sharding/         分片管理
│   ├── watermark/        水印设置
│   └── deploy/           部署管理
```

---

## 8. 缺失功能清单（按优先级）

### P0（功能闭环缺口）

| ID | 功能 | 说明 | 影响 |
|----|------|------|------|
| P0-1 | 增量设备发现 | 定时检测新增设备而非每次全量扫描 | 自动化程度 |
| P0-2 | WMI/WinRM 采集 | Windows 服务器性能指标采集 | Windows 监控闭环 |
| P0-3 | 通知对象精细化 | 按告警类型/级别/设备精准通知 | 告警通知准确性 |

### P1（完整度提升）

| ID | 功能 | 说明 |
|----|------|------|
| P1-1 | 趋势告警 | 增长率/持续时间预测 |
| P1-2 | SLA 达成率统计 | 工单 SLA 达成率报表 |
| P1-3 | 采集模板导入导出 | 跨环境迁移 |
| P1-4 | 设备配置版本管理 | 配置文件变更审计 |
| P1-5 | 案例 AI 推荐 | 从历史案例中推荐相似处置 |
| P1-6 | 图表数据导出 | 性能趋势图导出 PNG/CSV |

### P2（架构优化）

| ID | 问题 | 说明 |
|----|------|------|
| P2-1 | asset.py / device_api.py 重复 | 95 vs 75 端点，大量重复 |
| P2-2 | api/main.py 490 行过重 | 建议拆分到 api/routes/ |
| P2-3 | config/ 6 个 YAML 分散 | 建议数据库化管理 |
| P2-4 | 分片路由 FK 约束 | `_remove_foreign_keys` 需改进 |

---

## 9. 文档体系

| 文档 | 说明 | 维护者 |
|------|------|--------|
| `README.md` | 项目入口，5 分钟了解全貌 | 自动同步 |
| `DESIGN.md` | 本文件，架构 + 模块设计 | 每次架构变更更新 |
| `SPEC.md` | 技术规范（枚举/字段/API 契约） | 每次规范变更更新 |
| `IMPLEMENTATION_STATUS.md` | 各模块实现状态 | 每次迭代更新 |
| `docs/DOCS_STRUCTURE.md` | 文档更新机制 | 规范建立后不变 |

详细历史变更见 `CHANGES.md`。

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-02 | 初始设计文档 |
| v2.0 | 2026-05-28 | 全面重构，整合所有分散文档，建立清晰模块边界 |
