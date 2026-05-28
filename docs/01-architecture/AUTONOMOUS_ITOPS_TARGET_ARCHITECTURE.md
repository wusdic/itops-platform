# ITOPS 最终版平台目标架构与重构规划方案

> 建议文件位置：`docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md`  
> 文档状态：current
> 是否为事实源：yes
> 融合说明：已客观吸收上传建议中关于 Docs as Code、ADR、OpenAPI 自动导出、DevSecOps、OpenTelemetry、Agentic Workflow、测试体系和离线部署的可用内容。
> 文档定位：本文件是 ITOPS 平台后续产品设计、架构重构、功能开发、代码取舍和验收评审的最高级别目标架构依据。  
> 核心原则：不迁就当前代码，不简单堆砌已有功能，而是从平台最终目标、客户真实问题、企业级工程可落地性出发，重新定义 ITOPS 应该成为怎样的平台。

---

## 1. 平台定位

ITOPS 不应被理解为“设备管理、监控告警、工单、自动化、AI 助手”的简单组合。它应该被定位为：

> 面向私有化部署场景的自治运维操作系统。平台通过统一资源模型、统一配置模型、统一状态模型、统一事件模型、统一策略模型、统一执行模型和统一知识模型，把传统割裂的资产管理、配置管理、监控采集、日志分析、告警处置、工单协同、自动化执行和 AI 诊断整合为一个可持续演进的自治运维闭环。

该平台重点解决中小型政企、园区、医院、学校、制造企业、集团分支机构和内部 IT 团队的典型问题：

1. 不清楚有哪些设备、服务、系统、数据库、中间件和接口。
2. 资产台账静态化，无法反映实时运行状态。
3. 配置散落在系统、脚本、文档和人员经验中，无法统一管理。
4. 故障发现依赖人工巡检或用户投诉。
5. 告警多、噪声大、无法判断影响范围和优先级。
6. 问题定位依赖少数有经验人员。
7. 处置脚本零散，执行过程不可控、不可审计、不可回滚。
8. 工单只是记录结果，不能沉淀可复用的处置能力。
9. AI 如果只作为聊天工具，无法真正进入运维闭环。
10. 文档、代码、配置和实际平台状态长期不一致。

因此，ITOPS 的最终目标不是“做很多页面”，而是让平台具备以下能力：

```text
自动发现资源
  ↓
自动纳管资产
  ↓
统一配置和凭证
  ↓
持续采集状态、指标、日志和配置事实
  ↓
自动识别异常和事件
  ↓
自动收敛告警并判断影响范围
  ↓
自动构造故障上下文
  ↓
AI 辅助分析根因和推荐处置方案
  ↓
策略引擎判断是否可自动执行
  ↓
自动化引擎安全执行、实时回传日志、验证结果
  ↓
失败时自动回滚或升级工单
  ↓
关闭告警、沉淀知识、优化策略
```

---

## 2. 平台建设总原则

### 2.1 不以当前代码为边界，以目标架构为边界

现有代码只能作为素材，不能作为约束。判断某个模块是否保留、修改、重构或删除，应看它是否服务目标自治闭环，而不是看它已经写了多少代码。

判断标准如下：

| 判断维度 | 保留 | 修改/适配 | 重构 | 删除/归档 |
|---|---|---|---|---|
| 是否服务自治闭环 | 已经能进入闭环 | 功能有价值但接口或模型不统一 | 与目标方向一致但边界混乱 | 与目标无关或过时 |
| 模块边界 | 领域职责清楚 | 局部混杂 | 路由、业务、数据访问混在一起 | 临时实验或重复实现 |
| 数据模型 | 支持历史、状态、审计、关联 | 字段需补充 | 模型无法支撑未来能力 | 字段含义混乱且无复用价值 |
| 可观测性 | 有状态、日志、trace_id | 日志不足 | 无过程记录 | 无法排障 |
| 可编排性 | 可被策略或自动化调用 | 需封装成服务 | 只能页面人工触发 | 孤立功能 |
| 安全性 | 有权限、审批、审计、凭证保护 | 需补强 | 存在明显风险 | 高风险且无保留价值 |

### 2.2 先做平台底座，再做功能扩张

后续不应继续盲目增加页面和接口。应先建设平台底座：

1. 统一资源模型。
2. 统一配置模型。
3. 统一采集与状态模型。
4. 统一事件模型。
5. 统一告警生命周期。
6. 统一策略模型。
7. 统一自动化执行模型。
8. 统一日志与审计模型。
9. 统一 AIops 上下文模型。
10. 统一知识沉淀模型。

只有这些底座清楚，后续增加采集器、页面、策略、脚本、报表才不会继续形成技术债。

### 2.3 所有功能必须进入闭环

任何功能设计都要回答九个问题：

1. 它管理什么对象？
2. 它依赖什么配置？
3. 它采集什么数据？
4. 它如何判断状态？
5. 它是否生成事件？
6. 它是否触发策略？
7. 它是否能执行动作？
8. 它是否记录日志和审计？
9. 它是否能沉淀知识或优化策略？

无法进入闭环的功能，应降低优先级。

---

## 3. 平台总体闭环

### 3.1 自治运维主闭环

```text
资源发现
  ↓
资产纳管
  ↓
配置建模
  ↓
凭证绑定
  ↓
采集模板绑定
  ↓
实时采集
  ↓
状态更新
  ↓
事件生成
  ↓
告警收敛
  ↓
影响分析
  ↓
AI 根因分析
  ↓
策略匹配
  ↓
风险判断
  ↓
审批 / 自动执行
  ↓
实时日志回传
  ↓
结果验证
  ↓
回滚 / 升级 / 关闭
  ↓
工单复盘
  ↓
知识沉淀
  ↓
策略优化
```

### 3.2 平台核心对象流

```text
Asset 资产
  ├── 绑定 Config 配置
  ├── 产生 State 状态
  ├── 产生 Metric 指标
  ├── 产生 Log 日志
  ├── 触发 Event 事件
  ├── 生成 Alert 告警
  ├── 命中 Policy 策略
  ├── 触发 Execution 执行
  ├── 关联 Ticket 工单
  └── 沉淀 Knowledge 知识
```

### 3.3 最小可验证闭环场景

第一阶段建议选择“Linux 磁盘空间异常自动处置”作为最小闭环场景：

```text
Linux 资产纳管
  ↓
绑定 SSH 凭证和磁盘采集模板
  ↓
采集磁盘使用率
  ↓
写入时序库和状态中心
  ↓
超过阈值生成 disk_usage_high 事件
  ↓
事件生成告警
  ↓
告警详情聚合资产、指标、日志、历史执行、配置变更
  ↓
AI 生成结构化根因分析
  ↓
策略中心命中“磁盘清理策略”
  ↓
判断环境、风险、时间窗口和审批要求
  ↓
执行 dry-run
  ↓
低风险自动执行 / 高风险进入审批
  ↓
执行日志实时回传
  ↓
重新采集磁盘指标验证结果
  ↓
成功关闭告警，失败升级工单或回滚
  ↓
生成知识案例草稿
```

该场景能同时验证资产、配置、采集、状态、事件、告警、策略、自动化、日志、AI、工单和知识库，是最适合作为平台主干的 MVP。

---

## 4. 七个统一模型

ITOPS 的底层不应是页面集合，而应是七个统一模型。

### 4.1 统一资源模型 Resource Model

资源模型回答“平台管理什么”。

资源类型包括：

- 物理服务器。
- 虚拟机。
- 网络设备。
- 安全设备。
- 存储设备。
- 数据库。
- 中间件。
- Web 服务。
- API 服务。
- 进程。
- 端口。
- 容器。
- Kubernetes 工作负载。
- 云资源。
- 业务系统。
- 外部依赖系统。

资源模型必须支持：

- 基础属性。
- IP 和管理地址。
- 类型与子类型。
- 厂商和型号。
- 环境：生产、测试、开发、灾备。
- 区域、机房、机柜。
- 负责人。
- 运维组。
- 标签。
- 分组。
- 生命周期。
- 纳管状态。
- 可达状态。
- 健康状态。
- 关系依赖。
- 凭证绑定。
- 采集模板绑定。
- 策略绑定。
- 自动化能力声明。

### 4.2 统一配置模型 Configuration Model

配置模型回答“平台期望系统如何运行”。

配置对象包括：

- 采集模板。
- 指标阈值。
- 日志解析规则。
- 告警规则。
- 通知规则。
- 自动化策略。
- 脚本参数。
- 执行凭证。
- AI 提示词模板。
- 知识检索范围。
- 权限策略。
- 审批策略。
- 维护窗口。

配置模型必须支持：

- 配置分类。
- 配置版本。
- 配置发布。
- 配置灰度。
- 配置回滚。
- 配置继承：全局 → 租户 → 业务系统 → 分组 → 资产。
- 配置差异对比。
- 配置引用关系。
- 配置影响范围。
- 配置审计。
- 配置漂移检测。

### 4.3 统一状态模型 State Model

状态模型回答“对象现在怎么样”。

必须区分：

| 状态类型 | 含义 |
|---|---|
| 生命周期状态 | planned、active、retired |
| 纳管状态 | unmanaged、managed、partial |
| 可达状态 | reachable、unreachable、unknown |
| 健康状态 | healthy、warning、critical、maintenance |
| 采集状态 | success、partial_success、failed、timeout |
| 执行状态 | created、running、verifying、success、failed、rollback |
| 平台组件状态 | normal、degraded、unavailable |

状态中心必须支持：

- 最新状态缓存。
- 状态历史。
- 状态变更事件。
- 状态订阅。
- WebSocket 推送。
- 状态快照。
- 状态影响分析。
- 状态恢复验证。

### 4.4 统一事件模型 Event Model

事件模型回答“发生了什么”。

事件类型包括：

- 资产发现事件。
- 资产消失事件。
- 配置变更事件。
- 配置漂移事件。
- 采集成功/失败事件。
- 指标异常事件。
- 日志命中事件。
- 服务异常事件。
- 自动化执行事件。
- 审批事件。
- 工单事件。
- AI 分析事件。
- 平台组件异常事件。

事件必须包含：

- event_id。
- event_type。
- source。
- asset_id。
- severity。
- timestamp。
- payload。
- correlation_key。
- trace_id。
- status。
- related_objects。

事件流向：

```text
raw signal → normalized event → correlated event → alert / policy / ticket / audit
```

### 4.5 统一策略模型 Policy Model

策略模型回答“发生这种情况时应该怎么处理”。

策略至少包含：

- 触发源。
- 触发条件。
- 适用范围。
- 时间窗口。
- 前置条件。
- 排除条件。
- 风险等级。
- 审批要求。
- 动作链。
- 验证条件。
- 失败处理。
- 回滚动作。
- 通知规则。
- 优先级。
- 冲突处理。
- 命中解释。
- 版本。
- 发布状态。

策略必须支持：

- 策略模板。
- 策略版本。
- 策略启停。
- 策略灰度。
- 策略模拟。
- 策略冲突检测。
- 策略命中解释。
- 策略执行历史。
- 策略成功率统计。
- 策略误触发分析。

### 4.6 统一执行模型 Execution Model

执行模型回答“平台如何安全地采取动作”。

执行对象包括：

- 命令。
- 脚本。
- Playbook。
- API 调用。
- 服务重启。
- 配置回滚。
- 文件清理。
- 健康检查。
- 巡检。
- 备份。
- 基线检查。

执行模型必须支持：

- execution_id。
- 触发来源。
- 目标资产。
- 执行参数。
- 风险评估。
- dry-run。
- 审批。
- 并发锁。
- 灰度执行。
- 执行步骤。
- 实时 stdout/stderr。
- 超时。
- 重试。
- 回滚点。
- 后置验证。
- 执行结果。
- 审计记录。

执行状态机：

```text
created
  ↓
validated
  ↓
risk_assessed
  ↓
dry_run_completed
  ↓
waiting_approval
  ↓
approved / rejected
  ↓
queued
  ↓
running
  ↓
verifying
  ↓
success / failed / partial_success
  ↓
rollback_running / rollback_success / rollback_failed
  ↓
closed
```

### 4.7 统一知识模型 Knowledge Model

知识模型回答“这次经验如何复用”。

知识对象包括：

- SOP。
- 故障案例。
- 自动化剧本说明。
- 工单复盘。
- 执行失败经验。
- 设备厂商知识。
- 脚本使用说明。
- AI 分析反馈。
- 策略优化建议。

知识模型必须支持：

- 人工创建。
- 工单转知识。
- 告警转知识。
- 执行记录转知识。
- AI 生成草稿。
- 审核发布。
- 版本管理。
- 标签。
- 适用范围。
- 关联资产类型。
- 关联告警类型。
- 关联策略。
- 关联脚本。
- 向量检索。
- 相似案例推荐。

---

## 5. 总体技术架构

### 5.1 分层架构

```text
表现层
  ├── Web Console
  ├── 运维指挥台
  ├── 故障处置台
  ├── 自动化编排台
  └── 移动/通知入口

接入层
  ├── API Gateway
  ├── Auth Middleware
  ├── RBAC/ABAC
  ├── WebSocket Gateway
  └── OpenAPI

应用服务层
  ├── Asset Service
  ├── Config Service
  ├── Collector Service
  ├── State Service
  ├── Event Service
  ├── Alert Service
  ├── Log Service
  ├── Policy Service
  ├── Automation Service
  ├── AIops Service
  ├── Ticket Service
  ├── Knowledge Service
  └── Governance Service

执行与调度层
  ├── Scheduler
  ├── Worker Pool
  ├── Collector Runtime
  ├── Automation Runtime
  ├── Policy Runtime
  ├── Notification Worker
  └── AI Task Worker

数据层
  ├── Relational DB
  ├── Time-series DB
  ├── Log Store
  ├── Redis
  ├── Object Storage
  ├── Vector Store
  └── Message Queue

被管环境
  ├── Agentless Assets
  ├── Server Agents
  ├── Edge Collectors
  ├── Network Devices
  ├── Databases
  ├── Middleware
  └── Application Services
```

### 5.2 后端目录建议

```text
backend/
  api/
    routers/
    schemas/
    dependencies/
    middleware/

  app/
    domains/
      asset/
      config/
      collector/
      state/
      event/
      alert/
      log/
      policy/
      automation/
      aiops/
      ticket/
      knowledge/
      governance/

    services/
    workflow/
    workers/
    integrations/
    common/

  infra/
    database/
    cache/
    queue/
    time_series/
    log_store/
    object_storage/
    vector_store/
    scheduler/
```

每个领域模块统一结构：

```text
domain/
  models.py
  schemas.py
  repository.py
  service.py
  events.py
  policies.py
  tasks.py
  handlers.py
  tests/
```

路由层只做：

1. 入参校验。
2. 鉴权。
3. 调用 service。
4. 返回统一响应。

业务流程不得继续堆在 API 路由文件中。

### 5.3 前端目录建议

```text
frontend/src/
  app/
    router/
    store/
    permission/
    layout/

  features/
    command-center/
    asset-config/
    monitoring-event/
    incident-response/
    automation-orchestration/
    aiops/
    ticket/
    knowledge/
    platform-admin/

  shared/
    api/
    components/
    hooks/
    utils/
    types/
    constants/
```

前端不应按后端接口堆页面，而应按运维工作流组织。

---

## 6. 数据架构

### 6.1 数据存储分工

| 数据类型 | 推荐存储 | 说明 |
|---|---|---|
| 资产、配置、策略、工单、用户、审批 | MySQL/PostgreSQL | 强一致、关系清楚 |
| 指标、状态趋势 | Prometheus/VictoriaMetrics/TimescaleDB | 高频时序数据 |
| 设备日志、执行日志、采集日志、审计日志 | OpenSearch/Elasticsearch/Loki | 检索和聚合 |
| 最新状态、锁、队列状态、WebSocket 会话 | Redis | 实时缓存 |
| 报告、附件、归档日志、脚本包 | MinIO/本地对象存储 | 大文件 |
| 知识库向量、相似案例 | Milvus/Qdrant/Chroma/pgvector | 语义检索 |
| 事件流、任务流、日志流 | Redis Stream/RabbitMQ/Kafka | 异步解耦 |

### 6.2 数据流

```text
Collector / Agent / Edge Collector
  ↓
标准化采集结果
  ├── 指标 → 时序库
  ├── 日志 → 日志库
  ├── 最新状态 → Redis + State 表
  ├── 资产事实 → Asset Center
  ├── 配置事实 → Config Drift
  └── 异常信号 → Event Center
```

### 6.3 数据设计原则

1. 高频指标不写入关系库。
2. 最新状态必须缓存化。
3. 历史状态必须可追溯。
4. 执行日志必须按 execution_id 聚合。
5. 审计日志必须不可随意修改。
6. 向量库不是事实源，知识原文仍由关系库或对象存储管理。
7. 所有异步任务必须有 trace_id。
8. 所有自动化执行必须有完整过程日志。
9. 所有配置变更必须有版本和审计。

---

## 7. Agent、Agentless 与边缘采集器

### 7.1 Agentless 模式

适合快速接入和轻量部署。

支持：

- ICMP。
- TCP。
- SNMP。
- SSH。
- WMI/WinRM。
- REST API。
- IPMI。
- Redfish。
- Syslog。
- 数据库连接。
- VMware API。
- Kubernetes API。

优点是部署快、侵入低；缺点是实时性和深度受限。

### 7.2 Agent 模式

适合需要深度采集和自动化执行的服务器。

Agent 能力：

- 本地指标采集。
- 本地日志采集。
- 服务状态采集。
- 文件变化检测。
- 本地脚本执行。
- 实时执行日志回传。
- 心跳上报。
- 离线缓存。
- 策略下发。
- 自升级。

### 7.3 边缘采集器模式

适合多机房、多网段、内外网隔离、安全域隔离场景。

边缘采集器能力：

- 本区域资产发现。
- 本区域采集任务执行。
- 本区域日志转发。
- 本地缓存。
- 断点续传。
- 与中心平台安全通信。
- 采集器健康上报。
- 采集器版本管理。

### 7.4 采集器框架要求

所有采集器必须符合统一接口：

```python
class BaseCollector:
    def validate_config(self, config): ...
    def test_connection(self, target, credential): ...
    def collect(self, target, config, context): ...
    def parse(self, raw_result): ...
    def normalize(self, parsed_result): ...
```

统一输出：

```json
{
  "collector": "ssh",
  "target_asset_id": "asset-001",
  "status": "success",
  "metrics": [],
  "logs": [],
  "facts": {},
  "errors": [],
  "started_at": "2026-01-01T00:00:00",
  "finished_at": "2026-01-01T00:01:00",
  "trace_id": "trace-001"
}
```

---

## 8. 核心领域模块设计

## 8.1 资产中心 Asset Center

### 目标

资产中心是平台的基础账本，不是简单设备表。它要管理平台中所有可观测、可配置、可告警、可执行的对象。

### 功能

- 资产发现。
- 资产纳管。
- 资产分组。
- 资产标签。
- 资产关系。
- 业务系统映射。
- 生命周期管理。
- 纳管状态。
- 可达状态。
- 健康状态。
- 资产画像。
- 凭证绑定。
- 采集模板绑定。
- 策略绑定。
- 自动化能力声明。
- 影响范围分析。

### 关键表

- `assets`
- `asset_ips`
- `asset_tags`
- `asset_groups`
- `asset_relations`
- `asset_credentials`
- `asset_collection_profiles`
- `asset_policy_bindings`
- `asset_lifecycle_events`

### 现有代码处理方向

现有 asset/device 相关能力应统一到资产中心。`device` 不应作为与 `asset` 并列的主模型，而应作为 asset 的一种类型或兼容视图。

---

## 8.2 配置与凭证中心 Config Center

### 目标

配置中心管理平台“期望状态”。所有采集配置、阈值、通知、脚本参数、策略、凭证、AI 模板都必须统一管理。

### 功能

- 配置分类。
- 配置模板。
- 配置版本。
- 配置继承。
- 配置发布。
- 配置灰度。
- 配置回滚。
- 配置差异。
- 配置引用检查。
- 配置影响范围。
- 配置审计。
- 凭证加密。
- 凭证轮换。
- 配置漂移检测。

### 配置漂移

必须区分：

```text
期望配置 Desired Configuration
实际配置 Actual Configuration
配置漂移 Drift
配置变更 Change
配置发布 Release
配置回滚 Rollback
```

漂移示例：

```text
期望：nginx 应运行，443 端口应开放
实际：nginx 未运行，443 不可达
结果：服务运行状态漂移
```

### 关键表

- `config_definitions`
- `config_versions`
- `config_releases`
- `config_bindings`
- `config_drifts`
- `credentials`
- `credential_bindings`
- `change_records`
- `change_approvals`

---

## 8.3 采集与状态中心 Collector & State Center

### 目标

采集中心负责感知现实环境；状态中心负责回答“现在怎么样”。

### 功能

- 多协议采集。
- 采集任务。
- 采集调度。
- 采集器注册。
- 采集器健康。
- 采集结果标准化。
- 最新状态。
- 状态历史。
- 状态变更。
- 状态推送。
- 状态快照。
- 状态恢复验证。

### 关键表

- `collector_instances`
- `collector_capabilities`
- `collection_jobs`
- `collection_job_targets`
- `collection_results`
- `collection_job_logs`
- `asset_state_snapshots`
- `asset_state_changes`
- `metric_points`
- `service_status`

---

## 8.4 事件与告警中心 Event & Alert Center

### 目标

事件中心是平台神经系统，告警是事件处理后的结果之一。

### 功能

- 事件标准化。
- 事件去重。
- 事件关联。
- 事件分级。
- 事件路由。
- 告警生成。
- 告警收敛。
- 告警抑制。
- 告警静默。
- 告警升级。
- 告警转工单。
- 告警触发策略。
- 告警生命周期。
- 告警复盘。

### 关键表

- `events`
- `event_rules`
- `event_correlations`
- `alerts`
- `alert_rules`
- `alert_suppression_rules`
- `alert_escalation_rules`
- `alert_timelines`
- `alert_related_events`

---

## 8.5 日志与可观测中心 Log & Observability Center

### 目标

日志中心不仅是日志查询页面，而是故障分析、执行审计和自动化闭环的证据中心。

### 日志类型

- 设备日志。
- 应用日志。
- 系统日志。
- Syslog。
- 采集过程日志。
- 自动化执行日志。
- 平台运行日志。
- 用户审计日志。
- AI 分析日志。

### 功能

- 日志采集。
- 日志解析。
- 日志标准化。
- 日志检索。
- 日志实时流。
- 日志规则匹配。
- 日志与事件关联。
- 日志与告警关联。
- 日志与执行关联。
- 日志与工单关联。
- 日志脱敏。
- 日志留存。
- 日志归档。
- AI 日志解释。

### 执行日志要求

每次执行必须形成：

```text
execution_id
  ├── trigger_source
  ├── policy_id
  ├── playbook_id
  ├── script_version
  ├── target_assets
  ├── parameters
  ├── approval_id
  ├── step logs
  ├── stdout stream
  ├── stderr stream
  ├── exit_code
  ├── duration
  ├── final_status
  └── audit_record
```

### 关键表

- `logs_raw`
- `logs_parsed`
- `log_rules`
- `log_stream_sessions`
- `execution_logs`
- `execution_log_chunks`
- `audit_logs`
- `trace_spans`

---

## 8.6 策略与规则中心 Policy Engine

### 目标

策略中心决定“发生某类事件时平台应该做什么”。

### 功能

- 策略模板。
- 策略创建。
- 策略版本。
- 策略启停。
- 策略发布。
- 策略灰度。
- 策略模拟。
- 策略冲突检测。
- 策略命中解释。
- 策略优先级。
- 策略执行历史。
- 策略成功率统计。
- 策略误触发分析。

### 策略示例

```yaml
name: Linux 磁盘空间自动清理
trigger:
  event_type: disk_usage_high
  condition:
    metric: disk_usage
    operator: ">"
    value: 90
    duration: 5m
scope:
  asset_type: linux_server
  env: non_production
risk:
  level: low
  require_approval: false
actions:
  - type: ai_analyze
  - type: dry_run
  - type: execute_playbook
    playbook: linux_disk_cleanup
  - type: verify
    metric: disk_usage
    operator: "<"
    value: 85
fallback:
  - type: create_ticket
  - type: notify
```

### 策略冲突示例

```text
策略 A：磁盘超过 90% 自动清理日志
策略 B：生产服务器禁止自动删除文件
处理结果：策略 B 优先，策略 A 只能生成建议和工单
```

---

## 8.7 自动化执行中心 Automation Engine

### 目标

自动化执行中心负责安全、可控、可追溯地执行处置动作。

### 功能

- 脚本库。
- 脚本版本。
- Playbook。
- 执行参数。
- 风险评估。
- dry-run。
- 审批。
- 并发锁。
- 灰度执行。
- 分批执行。
- 实时日志。
- 超时控制。
- 重试。
- 回滚。
- 结果验证。
- 执行复盘。
- 执行转知识。

### 企业级约束

- 幂等性。
- 并发锁。
- 高危命令黑名单。
- 自动执行白名单。
- 生产环境审批。
- 最大影响面控制。
- 维护窗口控制。
- 执行前快照。
- 执行后验证。
- 失败回滚。
- 无回滚动作必须提示风险。
- AI 不得绕过执行安全边界。

### 关键表

- `automation_playbooks`
- `automation_playbook_versions`
- `automation_scripts`
- `automation_script_versions`
- `automation_executions`
- `automation_execution_steps`
- `automation_execution_logs`
- `automation_approvals`
- `execution_locks`
- `execution_dry_runs`
- `execution_risk_assessments`
- `execution_snapshots`
- `execution_rollback_points`
- `execution_state_transitions`

---

## 8.8 AIops 与知识中心

### AIops 目标

AI 不应只是聊天助手，而应成为受控的诊断与决策辅助层。

### AI 输入上下文

- 资产信息。
- 资产关系。
- 业务系统。
- 当前状态。
- 指标趋势。
- 相关事件。
- 相关告警。
- 相关日志。
- 最近配置变更。
- 最近执行记录。
- 相关工单。
- 相似案例。
- 可用策略。
- 可执行动作。
- 风险边界。

### AI 输出要求

AI 输出必须结构化：

```json
{
  "summary": "故障摘要",
  "impact": "影响范围",
  "probable_causes": [
    {
      "cause": "日志增长过快导致磁盘空间不足",
      "confidence": 0.82,
      "evidence": ["disk_usage_metric", "log_growth_trend"]
    }
  ],
  "recommended_actions": [
    {
      "action": "执行日志压缩和清理",
      "risk": "low",
      "requires_approval": false
    }
  ],
  "verification_plan": ["重新采集磁盘使用率", "检查服务状态"],
  "uncertainties": ["未获取应用日志保留策略"]
}
```

### AI 权限边界

AI 可以：

- 分析。
- 总结。
- 推荐。
- 解释。
- 生成知识草稿。
- 调用只读工具。
- 在策略允许下提出执行请求。

AI 不能：

- 绕过审批。
- 直接执行高危动作。
- 读取明文凭证。
- 修改安全策略。
- 删除数据。
- 无证据下强行给结论。

### 知识中心功能

- SOP。
- 故障案例。
- 工单转知识。
- 执行记录转知识。
- AI 生成知识草稿。
- 知识审核。
- 版本管理。
- 向量检索。
- 相似案例推荐。
- 策略优化建议。

---

## 8.9 工单与协同中心 Ticket Center

### 目标

工单是自动化闭环中的人工协同层，不是独立记录系统。

### 功能

- 告警转工单。
- 策略触发工单。
- 自动化失败转工单。
- 人工创建工单。
- 自动派单。
- SLA。
- 升级。
- 审批。
- 评论。
- 附件。
- 时间线。
- 关联告警。
- 关联事件。
- 关联日志。
- 关联执行。
- 关联知识。
- 复盘总结。
- 工单转知识。

---

## 8.10 平台治理中心 Governance Center

### 目标

确保平台可部署、可维护、可扩展、可审计、可安全运行。

### 功能

- 用户。
- 角色。
- 权限。
- 租户。
- 菜单。
- 字典。
- API Key。
- 凭证加密。
- 系统参数。
- 审计日志。
- 备份恢复。
- 数据归档。
- 许可证。
- 安全基线。
- 平台健康。
- 组件状态。
- 一键自检。

---

## 9. 前端目标体验设计

### 9.1 前端一级工作台

前端应围绕用户工作流，而不是后端模块名组织：

```text
1. 运维指挥台
2. 资产与配置台
3. 监控与事件台
4. 故障处置台
5. 自动化编排台
6. AI 与知识台
7. 平台管理台
```

### 9.2 运维指挥台

一屏回答：

- 当前是否有严重故障？
- 哪些业务受影响？
- 哪些问题正在自动修复？
- 哪些动作需要人工确认？
- 哪些采集器或平台组件异常？
- 今日工单 SLA 是否有风险？

组件：

- 总体健康评分。
- 严重告警。
- 业务影响排行。
- 自动化执行中任务。
- 自动修复成功率。
- 采集成功率。
- 新增资产。
- 配置变更。
- 平台组件健康。
- AI 建议摘要。

### 9.3 资产与配置台

页面：

- 资产总览。
- 资产列表。
- 资产详情。
- 资产关系图。
- 发现任务。
- 发现结果确认。
- 凭证管理。
- 采集模板。
- 配置版本。
- 配置发布。
- 配置差异。
- 配置回滚。
- 配置漂移。
- 策略绑定。

资产详情页应展示：

- 基础信息。
- 当前状态。
- 采集状态。
- 指标趋势。
- 相关服务。
- 相关日志。
- 相关告警。
- 相关工单。
- 相关自动化执行。
- 绑定配置。
- 绑定策略。
- 历史变更。

### 9.4 监控与事件台

页面：

- 实时状态。
- 指标监控。
- 日志检索。
- 事件流。
- 告警中心。
- 告警规则。
- 事件规则。
- 告警收敛。
- 维护窗口。
- 影响分析。

告警详情必须展示完整证据链：

- 触发指标。
- 趋势图。
- 相关日志。
- 相关事件。
- 资产关系。
- AI 分析。
- 推荐动作。
- 可执行剧本。
- 执行历史。
- 工单状态。

### 9.5 故障处置台

这是平台核心竞争力页面，建议采用“一案到底”结构：

```text
左侧：故障时间线
中间：证据与分析
右侧：推荐动作与执行控制
底部：实时日志流
```

必须包含：

- 告警摘要。
- 影响范围。
- 资产关系。
- 指标趋势。
- 日志片段。
- 配置变更。
- 最近执行记录。
- AI 根因分析。
- 推荐处置方案。
- 风险提示。
- 审批按钮。
- 执行按钮。
- 实时日志。
- 验证结果。
- 转工单。
- 生成知识案例。

### 9.6 自动化编排台

页面：

- 脚本库。
- Playbook 管理。
- 策略编排。
- 策略模拟。
- dry-run。
- 执行历史。
- 实时执行控制台。
- 审批中心。
- 回滚记录。
- 自动化效果统计。

策略编排可先不用复杂拖拽，先用分步表单：

1. 选择触发条件。
2. 选择适用范围。
3. 选择动作。
4. 设置风险和审批。
5. 设置验证条件。
6. 设置失败处理。
7. 策略模拟。
8. 发布。

### 9.7 配置发布台

必须支持：

- 配置编辑。
- 配置差异。
- 影响资产列表。
- 发布范围。
- 灰度发布。
- 审批。
- 发布日志。
- 回滚版本。
- 发布后验证。

### 9.8 策略模拟台

必须支持：

- 选择策略。
- 选择测试资产。
- 选择历史事件。
- 展示命中结果。
- 展示动作链路。
- 展示风险。
- 展示审批要求。
- 展示冲突策略。
- 展示预计影响面。

---

## 10. 平台自身运维

平台必须具备自监控和自诊断能力。

### 10.1 组件健康

需要监控：

- API Server。
- Web 前端。
- Scheduler。
- Worker。
- Collector。
- Event Bus。
- Redis。
- MySQL。
- 时序库。
- 日志库。
- 对象存储。
- 向量库。
- LLM 服务。
- WebSocket 服务。
- 通知服务。

### 10.2 平台自身指标

- API 延迟。
- API 错误率。
- 队列积压。
- 任务失败率。
- 采集成功率。
- 采集超时率。
- 执行任务成功率。
- 通知发送成功率。
- AI 分析成功率。
- WebSocket 连接数。
- 数据库连接池。
- 存储使用率。

### 10.3 一键自检

自检内容：

- 数据库连接。
- Redis 连接。
- 队列状态。
- LLM 状态。
- 采集器状态。
- 通知通道。
- 凭证加密配置。
- 存储空间。
- 后台任务。
- 许可证状态。

---

## 11. 外部集成能力

平台应支持与客户现有系统集成：

- LDAP / AD。
- OAuth2 / OIDC。
- 企业微信 / 钉钉 / 飞书。
- 邮件 / SMS / Webhook。
- Prometheus。
- Zabbix。
- Grafana。
- ELK / OpenSearch。
- CMDB。
- ITSM。
- Kubernetes。
- VMware。
- 云厂商 API。
- 堡垒机。
- Git。
- CI/CD。

集成原则：

1. 使用 adapter 模式。
2. 业务逻辑不直接依赖第三方系统。
3. 集成必须支持连接测试。
4. 集成必须支持失败重试。
5. 集成必须有审计日志。
6. 集成凭证必须进入凭证中心。

---

## 12. 验收指标体系

### 12.1 运维效果指标

| 指标 | 含义 | 初期目标 |
|---|---|---|
| 资产发现覆盖率 | 已发现资产 / 实际资产 | 80%+ |
| 资产纳管率 | 已纳管资产 / 已发现资产 | 70%+ |
| 采集成功率 | 成功采集 / 总采集 | 95%+ |
| 告警压缩率 | 收敛前告警 / 收敛后告警 | 持续提升 |
| MTTD | 平均发现故障时间 | 持续下降 |
| MTTA | 平均响应时间 | 持续下降 |
| MTTR | 平均修复时间 | 持续下降 |
| 自动化处置成功率 | 自动化成功关闭问题比例 | 持续提升 |
| 自动化回滚成功率 | 回滚成功比例 | 95%+ |
| AI 分析采纳率 | AI 建议被采纳比例 | 持续提升 |
| 策略误触发率 | 错误触发 / 总触发 | 持续下降 |

### 12.2 技术质量指标

- 核心 API 单元测试覆盖率。
- 领域服务集成测试覆盖率。
- 自动化执行可追溯率。
- 事件丢失率。
- 日志检索延迟。
- WebSocket 断线重连成功率。
- 队列积压恢复时间。
- 数据备份成功率。
- 灾难恢复时间。
- 前端关键页面加载时间。

---

## 13. 总体重构结论

1. ITOPS 应建设为自治运维操作系统，不是监控工单系统。
2. 平台主干是资源、配置、状态、事件、策略、执行、知识七个统一模型。
3. 现有功能应围绕闭环重组，而不是继续按已有目录扩张。
4. 配置中心、状态中心、事件中心、策略中心、执行日志中心是当前最关键缺口。
5. 自动化运维必须支持风险判断、审批、dry-run、实时日志、验证和回滚。
6. AI 必须受控、结构化、有证据链，不能替代策略和审批。
7. 前端必须围绕运维工作流，特别是故障处置台，而不是简单菜单堆叠。
8. 平台自身也必须可观测、可诊断、可恢复。
9. 文档必须形成单一事实源，避免旧文档继续干扰开发。
10. 第一阶段应围绕一个真实故障闭环完成主干重构，而不是同时铺开所有功能。


---

# 附加融合内容：来自上传建议的客观采纳项

## A. 客观采纳结论

对上传的 Qwen 方案进行复核后，可以借鉴的内容主要集中在企业级工程治理和私有化落地层面，而不是替代当前“自治运维操作系统”的主架构。结论如下：

### A.1 应融合的内容

1. **Docs as Code**：将文档纳入代码工程治理，要求 PR 修改代码时同步更新文档。
2. **docs-check CI**：在 GitHub Actions 中增加文档检查，防止代码和文档再次脱节。
3. **OpenAPI 自动导出**：API 文档不应手工维护，应由 FastAPI 自动生成 `openapi.json` 并在 release 时发布。
4. **ADR 架构决策记录**：重大技术选型、数据库选择、消息队列选择、AI Agent 框架选择、安全边界变更必须记录决策背景和影响。
5. **DevSecOps**：增加依赖漏洞扫描、Secret 扫描、镜像扫描、静态检查、权限测试和高危自动化命令检查。
6. **平台自身可观测性**：引入 OpenTelemetry，对 FastAPI 请求、Worker/Celery 任务、数据库连接池、队列积压、AI 调用和自动化执行链路进行观测。
7. **更明确的技术选型建议**：前端 TypeScript、Vite、Pinia、Element Plus；后端 SQLAlchemy 2.0、Pydantic V2、Alembic；时序库可优先 VictoriaMetrics；向量库可优先 Qdrant/Chroma/pgvector。
8. **Agentic Workflow 作为中后期 AIops 增强方向**：可以基于 LangGraph 设计 AI 工具调用，但必须 Human-in-the-loop，不允许 AI 直接绕过策略和审批。
9. **本地化/离线部署专项设计**：需要离线镜像包、Python wheelhouse、模型文件、install.sh、upgrade.sh、rollback.sh、数据库 migration、配置差异保留和升级回滚。
10. **测试体系强化**：pytest、testcontainers、Playwright/Cypress、基础混沌测试应纳入开发计划。
11. **凭证加密和动态脱敏**：设备密码、SSH Key、API Token 应加密存储，并对敏感字段做动态脱敏。
12. **高危操作二次确认**：生产环境、高危命令、批量执行应支持 MFA 或二次确认。

### A.2 不建议直接采纳或仅作为远期能力的内容

1. **eBPF 无侵入采集**：有价值，但复杂度高，当前主线应先完成多协议采集、状态中心和执行闭环，eBPF 作为后期增强。
2. **FinOps 成本分析**：适合云资源成本治理，但当前平台主线是自治运维闭环，不应第一阶段投入。
3. **多活高可用**：企业级价值高，但应在主干稳定后再做，不应压在 MVP 阶段。
4. **复杂低代码表单引擎**：可作为 ITSM 后期增强，第一阶段只做必要的工单字段配置。
5. **固定 Month 1-2 / Month 3-4 时间表**：不适合当前代码重构不确定性，应改为里程碑式推进。
6. **完全自主 AI Agent 执行修复**：方向可参考，但必须受策略引擎、审批、风险边界和审计约束。

---

## B. 融合后的技术选型补充

### B.1 前端技术栈

建议前端目标栈为：

- Vue 3。
- TypeScript。
- Vite。
- Pinia。
- Element Plus。
- TailwindCSS 可选，用于构建更灵活的工作台界面。
- Playwright 或 Cypress，用于 E2E 测试。
- 低代码表单引擎作为 ITSM 后期增强能力，不作为第一阶段主线。

### B.2 后端技术栈

建议后端目标栈为：

- Python 3.10+。
- FastAPI。
- SQLAlchemy 2.0。
- Pydantic V2。
- Alembic。
- Celery / Dramatiq / 自研轻量 Worker，根据任务复杂度选择。
- pytest。
- ruff、black、mypy 作为基础质量工具。

### B.3 数据与中间件选型

- 关系型数据库：PostgreSQL 15 或 MySQL 8.0。若当前项目已基于 MySQL，可继续使用 MySQL；如果未来需要更强 JSONB、并发和 RLS 能力，可评估 PostgreSQL。
- SQLite：只允许本地开发或测试，不允许生产使用。
- 时序数据库：VictoriaMetrics 或 Prometheus。私有化单机/小集群场景优先 VictoriaMetrics。
- 日志库：Loki / OpenSearch，根据部署资源和检索需求选择。
- 缓存与锁：Redis。
- 消息队列：第一阶段可用 Redis Streams，规模扩大后可引入 RabbitMQ。
- 对象存储：MinIO 或本地对象存储。
- 向量库：Qdrant / Chroma / pgvector。Milvus 仅在大规模场景考虑。
- AI 推理：Ollama / vLLM。
- AI Agent 编排：LangGraph 作为中后期方向，第一阶段先实现受控工具调用和人工确认。
- 可观测：OpenTelemetry。

---

## C. DevSecOps 与安全治理补充

### C.1 DevSecOps 基础能力

平台开发流程应加入：

- pre-commit。
- ruff / black。
- 依赖漏洞扫描。
- Secret 扫描。
- 镜像漏洞扫描。
- 静态代码检查。
- API 权限测试。
- 高危自动化命令检查。
- PR 安全检查清单。

### C.2 凭证保护

- 设备密码、SSH Key、API Token 必须加密存储。
- 推荐 AES-256-GCM。
- 主密钥不得写入代码或数据库，应通过环境变量、KMS 或部署密钥注入。
- 凭证读取、测试连接、使用过程必须审计。
- AI 不得读取明文凭证。
- 导出数据不得包含明文凭证。

### C.3 动态脱敏

敏感字段包括：

- 密码。
- Token。
- SSH Key。
- 手机号。
- 邮箱。
- IP 地址。
- 主机名。
- 客户名称。
- 业务系统名称。
- 日志中的密钥和账号。

脱敏应根据用户权限、访问场景、数据敏感级别动态控制。

### C.4 高危操作控制

以下动作必须进入强控制：

- 删除文件。
- 修改生产配置。
- 批量重启服务。
- 数据库写操作。
- 大批量资产执行命令。
- 关闭安全策略。
- 修改凭证。
- 执行自定义脚本。

控制方式包括：

- 高危命令黑名单。
- 自动执行白名单。
- 二次确认。
- MFA。
- 审批。
- dry-run。
- 维护窗口。
- 最大影响面限制。
- 回滚点。

---

## D. 平台自身可观测性补充

平台必须监控自身，而不是只监控客户资产。

### D.1 OpenTelemetry 接入范围

- FastAPI 请求链路。
- Worker / Celery 任务。
- 数据库查询耗时。
- Redis 调用。
- 外部集成调用。
- AI 工具调用。
- 自动化执行链路。
- WebSocket 连接状态。

### D.2 平台自身指标

- API 延迟。
- API 错误率。
- 队列积压。
- 任务失败率。
- 采集成功率。
- 采集超时率。
- 执行任务成功率。
- 通知发送成功率。
- AI 分析成功率。
- WebSocket 连接数。
- 数据库连接池。
- 存储使用率。
- LLM 推理延迟。
- Agent 在线率。

---

## E. AI Agentic Workflow 补充

AI Agent 方向可借鉴，但必须分阶段推进：

| 阶段 | 能力 | 安全边界 |
|---|---|---|
| A1 | 结构化分析和推荐动作 | 不调用执行工具 |
| A2 | 只读工具调用：查资产、指标、日志、告警、工单 | 只读权限、全量审计 |
| A3 | 生成执行计划 | 必须由策略中心校验 |
| A4 | 低风险动作自动执行 | 仅限策略白名单 |
| A5 | 高风险动作执行 | 必须 Human-in-the-loop、审批、MFA |

所有 AI 工具调用必须记录：

- tool_call_id。
- 输入参数。
- 输出结果。
- 触发用户。
- 是否人工确认。
- 策略校验结果。
- 执行结果。
- 审计日志。

---

## F. 私有化与离线部署补充

### F.1 离线交付包

离线包应包含：

- Docker 镜像。
- Python wheelhouse。
- 前端构建产物。
- 数据库初始化脚本。
- Alembic migration。
- 默认配置模板。
- 模型文件或模型部署说明。
- install.sh。
- upgrade.sh。
- rollback.sh。
- 自检脚本。

### F.2 一键部署检查项

install.sh 应检查：

- OS 版本。
- CPU/内存/磁盘。
- Docker/Podman。
- 端口占用。
- 文件句柄数。
- 内核参数。
- 数据目录权限。
- 环境变量。
- 数据库连接。
- Redis 连接。
- 模型服务状态。

### F.3 平滑升级

升级必须支持：

- 升级前备份。
- 数据库 migration。
- 配置差异比对。
- 用户数据保留。
- 版本回滚。
- 升级后自检。
- 兼容旧 API 的过渡期。

### F.4 本地模型部署

可支持：

- Ollama。
- vLLM。
- GGUF/AWQ 量化模型。
- 本地 Qwen/Llama 系列模型。
- CPU 推理降级模式。
- GPU 推理模式。
- 模型服务健康检查。

---

## G. 最终架构结论补强

融合上传建议后，最终架构结论应补充为：

1. ITOPS 应建设为自治运维操作系统，不是监控工单系统。
2. 平台主干是资源、配置、状态、事件、策略、执行、知识七个统一模型。
3. 现有功能应围绕闭环重组，而不是继续按已有目录扩张。
4. 配置中心、状态中心、事件中心、策略中心、执行日志中心是当前最关键缺口。
5. 自动化运维必须支持风险判断、审批、MFA、dry-run、实时日志、验证和回滚。
6. AI 必须受控、结构化、有证据链，不能替代策略和审批。
7. Agentic Workflow 可以作为中后期增强，但必须坚持 Human-in-the-loop。
8. 前端必须围绕运维工作流，特别是故障处置台，而不是简单菜单堆叠。
9. 平台自身也必须可观测、可诊断、可恢复。
10. 私有化部署、离线升级、安全合规和 DevSecOps 是企业级落地的必要条件。
11. 文档必须形成 Docs as Code、ADR 和单一事实源，避免旧文档继续干扰开发。
12. 第一阶段应围绕一个真实故障闭环完成主干重构，而不是同时铺开所有功能。
