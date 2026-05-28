# 代码清单 (CODE INVENTORY)

> 文档状态：current
> 适用版本：v2.0
> 最后更新：2026-05-28
> 维护人：ITOPS 开发团队
> 是否为事实源：yes

---

## 说明

本文档记录所有现有代码模块的处理决策：
- **keep**：功能有价值，方向正确，可直接纳入新架构
- **adapt**：有价值，但 API、模型、命名或输出格式需要统一
- **refactor**：功能方向正确，但业务逻辑混乱、重复、不可扩展
- **remove**：过期、重复、实验性、与目标架构不符

---

## 一、数据库表分析

### 1.1 资产与设备

| 表名 | 用途 | 行数 | 状态 | 处理决策 |
|------|------|------|------|----------|
| `devices` | 设备主表 | 24 | adapt | 与 asset 统一建模，作为兼容层 |
| `devices_t202605239779` | 分片表 | 0 | remove | 测试分片表，已废弃 |
| `business_systems` | 业务系统 | 0 | keep | 纳入资产中心 |
| `device_groups` | 设备分组 | 0 | keep | 纳入资产中心 |
| `device_metric_configs` | 指标配置 | 0 | adapt | 纳入配置中心 |
| `device_protocol_configs` | 协议配置 | 0 | adapt | 纳入配置中心 |

### 1.2 监控与告警

| 表名 | 用途 | 行数 | 状态 | 处理决策 |
|------|------|------|------|----------|
| `alerts` | 告警表 | 6 | adapt | 增加生命周期字段，重构告警详情 |
| `alert_rules` | 告警规则 | 0 | adapt | 升级为策略中心的一部分 |
| `alert_notifications` | 告警通知 | 0 | adapt | 改为策略动作 |
| `alert_audit_logs` | 告警审计 | 19 | keep | 保留，增加事件关联 |
| `performance_metrics` | 性能指标 | 2645 | adapt | 纳入状态中心，增加 asset_id |
| `performance_metrics_202506` | 分片指标 | 0 | adapt | 改为时序库存储 |
| `performance_metrics_202507` | 分片指标 | 0 | adapt | 改为时序库存储 |

### 1.3 自动化

| 表名 | 用途 | 行数 | 状态 | 处理决策 |
|------|------|------|------|----------|
| `automation_scripts` | 自动化脚本 | 4 | keep | 纳入自动化执行中心 |
| `automation_script_versions` | 脚本版本 | 6 | keep | 保留版本管理 |
| `automation_executions` | 执行记录 | 3 | adapt | 增加状态机、step logs |
| `automation_execution_logs` | 执行日志 | 0 | keep | 保留，改进实时性 |
| `automation_tasks` | 任务 | 0 | adapt | 改为执行任务 |
| `automation_trigger_rules` | 触发规则 | 0 | refactor | 重构为策略中心 |
| `automation_ai_decisions` | AI 决策记录 | 0 | keep | 保留审计 |

### 1.4 工单

| 表名 | 用途 | 行数 | 状态 | 处理决策 |
|------|------|------|------|----------|
| `work_orders` | 工单 | 18 | keep | 保留，增加关联字段 |
| `work_order_flows` | 工单流程 | 23 | keep | 保留 |
| `work_order_escalations` | 工单升级 | 0 | keep | 保留 |

### 1.5 知识库

| 表名 | 用途 | 行数 | 状态 | 处理决策 |
|------|------|------|------|----------|
| `kb_fault_cases` | 故障案例 | 13 | keep | 纳入知识中心 |
| `kb_sop_documents` | SOP 文档 | 22 | keep | 纳入知识中心 |
| `kb_categories` | 知识分类 | 11 | keep | 保留 |
| `kb_tags` | 知识标签 | 27 | keep | 保留 |
| `kb_document_chunks` | 文档块 | 0 | keep | 保留，向量检索 |
| `kb_document_reviews` | 审核记录 | 0 | keep | 保留 |

### 1.6 日志

| 表名 | 用途 | 行数 | 状态 | 处理决策 |
|------|------|------|------|----------|
| `log_items` | 日志 | 20079 | adapt | 升级为日志中心，增加关联字段 |
| `log_groups` | 日志分组 | 2000 | keep | 保留 |
| `operation_logs` | 操作日志 | 20954 | keep | 升级为审计日志 |
| `log_config` | 日志配置 | 13 | keep | 纳入配置中心 |

### 1.7 AI

| 表名 | 用途 | 行数 | 状态 | 处理决策 |
|------|------|------|------|----------|
| `ai_conversations` | AI 会话 | 21 | adapt | 改为分析上下文 |
| `ai_messages` | AI 消息 | 50 | adapt | 改为分析记录 |

### 1.8 系统

| 表名 | 用途 | 行数 | 状态 | 处理决策 |
|------|------|------|------|----------|
| `system_users` | 用户 | 14 | keep | 保留 |
| `api_keys` | API Key | 1 | keep | 保留 |
| `tenants` | 租户 | 4 | adapt | 保留，多租户支持 |
| `departments` | 部门 | 2 | keep | 保留 |
| `menus` | 菜单 | 2 | keep | 保留 |
| `dict_items` | 字典项 | 42 | keep | 保留 |
| `dict_types` | 字典类型 | 9 | keep | 保留 |
| `dashboard_layouts` | 仪表盘布局 | 3 | keep | 保留，升级为自定义布局 |
| `backup_records` | 备份记录 | 1 | keep | 保留 |
| `discovery_tasks` | 发现任务 | 2 | keep | 保留，纳入资产发现 |
| `notification_channels` | 通知渠道 | 0 | keep | 保留 |
| `notification_targets` | 通知目标 | 0 | keep | 保留 |
| `notification_target_rules` | 通知规则 | 0 | adapt | 改为策略动作 |
| `notification_logs` | 通知日志 | 0 | keep | 保留 |
| `notification_message` | 通知消息 | 0 | keep | 保留 |
| `maintenance_windows` | 维护窗口 | 1 | keep | 保留 |
| `inspection_tasks` | 巡检任务 | 0 | keep | 保留 |
| `inspection_check_items` | 巡检项 | 0 | keep | 保留 |
| `inspection_results` | 巡检结果 | 0 | keep | 保留 |
| `reports` | 报表 | 1 | keep | 保留 |
| `report_templates` | 报表模板 | 0 | keep | 保留 |
| `report_schedules` | 报表计划 | 0 | keep | 保留 |
| `fingerprint_template_versions` | 指纹模板 | 0 | keep | 保留 |
| `network_scan_configs` | 网络扫描配置 | 1 | keep | 保留 |
| `adapter_templates` | 适配器模板 | 0 | keep | 保留 |

---

## 二、模块分析

### 2.1 采集器 (modules/collection/)

| 模块 | 协议 | 状态 | 处理决策 |
|------|------|------|----------|
| `ssh_collector/` | SSH | keep | 改造为 BaseCollector 统一接口 |
| `snmp_collector/` | SNMP | keep | 改造为 BaseCollector 统一接口 |
| `wmi_collector/` | WMI/WinRM | keep | 改造为 BaseCollector 统一接口 |
| `ipmi_collector/` | IPMI | keep | 改造为 BaseCollector 统一接口 |
| `redfish_collector/` | Redfish | keep | 改造为 BaseCollector 统一接口 |
| `vmware_collector/` | VMware API | keep | 改造为 BaseCollector 统一接口 |
| `api_collector/` | REST API | keep | 改造为 BaseCollector 统一接口 |
| `db_collector/` | 数据库 | keep | 改造为 BaseCollector 统一接口 |
| `log_collector/` | 日志采集 | keep | 纳入日志中心 |
| `syslog_collector/` | Syslog | keep | 纳入日志中心 |
| `mq_collector/` | 消息队列 | keep | 纳入日志中心 |
| `elasticsearch_collector/` | ES | keep | 纳入日志中心 |
| `browser_automation/` | 浏览器 | remove | 实验性，与目标架构不符 |
| `discovery/` | 资产发现 | keep | 纳入资产发现流程 |
| `fingerprint/` | 指纹识别 | keep | 保留，辅助发现 |

### 2.2 业务模块 (modules/business/)

| 模块 | 用途 | 状态 | 处理决策 |
|------|------|------|----------|
| `asset_management/` | 资产管理 | adapt | 迁入 domains/asset |
| `monitoring/` | 监控 | adapt | 拆分为 state/event/alert |
| `notification/` | 通知 | adapt | 改为策略动作 |
| `workorder/` | 工单 | keep | 保留，升级关联 |
| `knowledge/` | 知识 | keep | 升级为知识中心 |
| `knowledge_base/` | 知识库 | keep | 升级为知识中心 |
| `ai_copilot/` | AI 助手 | adapt | 改为故障分析助手 |
| `dashboard/` | 仪表盘 | keep | 升级为运维指挥台 |
| `report_generator/` | 报表 | keep | 保留 |

### 2.3 自动化模块 (modules/automation/)

| 模块 | 用途 | 状态 | 处理决策 |
|------|------|------|----------|
| `script_executor/` | 脚本执行 | adapt | 纳入自动化执行中心，增加状态机 |
| `alert_trigger/` | 告警触发 | adapt | 改为策略触发 |
| `self_healing/` | 自愈 | adapt | 改为自动化执行 |
| `task_scheduler/` | 任务调度 | keep | 保留，改进调度 |

### 2.4 基础设施 (modules/foundation/)

| 模块 | 用途 | 状态 | 处理决策 |
|------|------|------|----------|
| `auth_manager/` | 认证授权 | keep | 保留，统一到 governance |
| `db_models/` | 数据模型 | adapt | 统一到 domains/*/models |

### 2.5 存储模块 (modules/storage/)

| 模块 | 用途 | 状态 | 处理决策 |
|------|------|------|----------|
| `redis_client/` | Redis | keep | 统一到 common/redis_client |
| `influxdb/` | 时序存储 | keep | 纳入状态中心 |
| `minio/` | 对象存储 | keep | 保留 |
| `qdrant/` | 向量存储 | keep | 纳入知识中心 |
| `tdengine/` | 时序库 | adapt | 改为 VictoriaMetrics/Prometheus |

---

## 三、API 路由决策汇总

| 状态 | 数量 | 占比 |
|------|------|------|
| keep | ~25 | ~15% |
| adapt | ~60 | ~35% |
| refactor | ~20 | ~12% |
| remove | ~5 | ~3% |

---

## 四、前端页面决策汇总

| 状态 | 数量 | 占比 |
|------|------|------|
| keep | ~25 | ~35% |
| adapt | ~20 | ~28% |
| refactor | ~5 | ~7% |
| archive | ~10 | ~14% |

---

## 五、立即可执行的清理项

### 5.1 删除文件

- `itops_platform.db` — 本地 SQLite 数据库文件，已移入 .gitignore
- `auto_trigger_log.py` — 临时脚本，待评估后归档

### 5.2 归档模块

- `src/_archive_20250516/` — 旧版组件，已归档

### 5.3 待删除表（数据已迁移或无数据）

- `devices_t202605239779` — 测试分片表

---

## 六、重构优先级

### P0（平台主干，必须重构）

1. `devices` → `assets` 统一模型
2. 告警规则 → 策略中心
3. 自动化执行 → 状态机 + 实时日志
4. 脚本执行 → Playbook 化

### P1（平台闭环关键）

1. 采集器统一 BaseCollector 接口
2. 状态中心（Redis + 时序库）
3. 事件中心
4. AI 分析结构化

### P2（完善平台）

1. 配置中心
2. 凭证中心
3. 知识中心
4. 工单增强

### P3（增强能力）

1. 前端工作流重构
2. DevSecOps 工具链
3. 离线部署包
4. OpenTelemetry
