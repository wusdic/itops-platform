# ITOPS 最终版详细开发计划、现有代码取舍与文档治理方案

> 建议文件位置：`docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md`  
> 文档状态：current
> 是否为事实源：yes
> 融合说明：已客观吸收上传建议中关于 docs-check、ADR、OpenAPI 自动化、pre-commit、测试体系、安全扫描、平台自身可观测和离线部署的可用内容。
> 文档定位：本文件根据《ITOPS 完整平台目标架构与重构规划方案》制定，回答三个问题：  
> 1. 下一步具体怎么开发；  
> 2. 现有代码哪些保留、哪些适配、哪些重构、哪些删除；  
> 3. 文档如何治理，避免随着项目更新再次混乱。  

---

## 1. 执行总原则

### 1.1 先冻结低价值扩张

在主干重构完成前，不建议继续新增零散页面、零散 API、零散脚本。否则代码量会增加，但平台闭环不会增强。

允许继续做的只有三类工作：

1. 修复阻塞启动、部署、登录、核心接口调用的 bug。
2. 围绕目标闭环补底座。
3. 围绕磁盘异常自动处置 MVP 做端到端开发。

### 1.2 以领域服务替代路由堆叠

后端重构目标：

```text
routes 只负责 HTTP
service 负责业务流程
repository 负责数据访问
worker 负责异步任务
event handler 负责事件处理
policy engine 负责决策
automation engine 负责执行
```

### 1.3 旧代码不立即全删，先分层接管

对现有代码采用四类处理：

| 类型 | 处理方式 |
|---|---|
| 保留 | 方向正确、边界清晰、能直接纳入新架构 |
| 适配 | 有价值，但 API、模型、命名或输出格式需要统一 |
| 重构 | 功能方向正确，但业务逻辑混乱、重复、不可扩展 |
| 删除/归档 | 过期、重复、实验性、与目标架构不符 |

---

## 2. 第一阶段目标：主干收敛

第一阶段不追求功能铺满，目标是完成平台主干：

```text
资产中心
配置中心
采集中心
状态中心
事件中心
告警中心
策略中心
自动化执行中心
日志中心
AIops 最小分析能力
```

并跑通一个完整场景：

```text
Linux 磁盘空间异常 → 告警 → AI 分析 → 策略命中 → dry-run → 执行 → 实时日志 → 验证 → 关闭 / 工单
```

---

## 3. 详细开发阶段

## 阶段 0：仓库清理与基线冻结

### 目标

让团队知道当前开发以哪个架构文档为准，停止旧文档和旧接口继续扩散。

### 工作项

1. 新建标准 docs 目录。
2. 将旧需求、旧设计、旧状态文档移动到 archive。
3. 根目录只保留入口文件。
4. 新增当前事实源文档。
5. 梳理 API 路由清单。
6. 梳理前端页面清单。
7. 梳理数据库表清单。
8. 梳理采集器清单。
9. 梳理自动化脚本和任务清单。
10. 给所有待处理代码打标签：keep / adapt / refactor / remove。

### 交付物

- `docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md`
- `docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md`
- `docs/99-archive/`
- `docs/05-implementation/CODE_INVENTORY.md`
- `docs/05-implementation/API_INVENTORY.md`
- `docs/05-implementation/FRONTEND_PAGE_INVENTORY.md`

### 验收标准

- README 只引用当前事实源文档。
- 旧文档不再作为开发依据。
- 所有旧文档顶部标注 archived。
- 项目团队能明确后续开发依据。

---

## 阶段 1：后端领域目录与统一基础设施

### 目标

建立新后端结构，让旧 API 能逐步迁移到领域服务。

### 新建目录

```text
backend/app/domains/
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
```

### 通用基础能力

需要先实现：

1. 统一响应结构。
2. 统一错误码。
3. trace_id。
4. 请求上下文。
5. 审计记录工具。
6. 权限校验装饰器。
7. 数据库 session 管理。
8. Redis 工具。
9. 消息队列抽象。
10. 后台任务封装。

### 统一响应

```json
{
  "success": true,
  "code": "OK",
  "message": "success",
  "data": {},
  "trace_id": "trace-001"
}
```

### 错误码分类

```text
ASSET_*
CONFIG_*
COLLECTOR_*
STATE_*
EVENT_*
ALERT_*
LOG_*
POLICY_*
AUTOMATION_*
AIOPS_*
TICKET_*
KNOWLEDGE_*
AUTH_*
SYSTEM_*
```

### 现有代码处理

| 现有类型 | 处理 |
|---|---|
| api/routes 下业务逻辑 | 逐步迁移到 service |
| 通用工具 | 检查后保留到 common |
| 数据库连接 | 保留但统一封装 |
| 权限逻辑 | 保留可用部分，统一到 governance/auth |
| 零散异常处理 | 改为统一错误码 |

### 验收标准

- 新领域目录建立完成。
- 至少 asset、config、automation 三个领域使用新结构。
- 新旧 API 可以并存。
- 新 API 返回统一响应。
- 每次请求有 trace_id。

---

## 阶段 2：资产中心重构

### 目标

统一 asset/device 概念，建立平台基础资源账本。

### 开发内容

1. 建立 `assets` 主表。
2. 建立资产 IP、标签、分组、关系表。
3. 建立资产状态字段。
4. 建立资产类型字典。
5. 建立资产详情 API。
6. 建立资产关系 API。
7. 建立资产策略绑定 API。
8. 建立资产凭证绑定 API。
9. 建立资产采集模板绑定 API。
10. 建立旧 device API 兼容层。

### 现有代码取舍

| 现有代码 | 判断 | 处理 |
|---|---|---|
| `asset.py` | 有价值 | 作为资产中心 API 参考，业务逻辑迁入 service |
| `device_api.py` | 与 asset 重复 | 改为兼容层，内部调用 asset service |
| `modules/business/asset_management` | 有价值但需检查边界 | 迁入 `domains/asset` |
| 发现结果中的设备对象 | 有价值 | 映射为 asset discovery result |
| 重复 CRUD 接口 | 技术债 | 合并后删除 |

### API 建议

```text
GET    /api/v1/assets
POST   /api/v1/assets
GET    /api/v1/assets/{id}
PUT    /api/v1/assets/{id}
DELETE /api/v1/assets/{id}
POST   /api/v1/assets/{id}/bind-credential
POST   /api/v1/assets/{id}/bind-collection-profile
POST   /api/v1/assets/{id}/bind-policy
GET    /api/v1/assets/{id}/state
GET    /api/v1/assets/{id}/timeline
GET    /api/v1/assets/{id}/relations
```

### 验收标准

- asset/device 不再双主线维护。
- 资产详情能看到基础信息、状态、配置绑定、策略绑定。
- 旧 device API 不再直接操作旧模型。
- 前端资产页面改用新 asset API。

---

## 阶段 3：配置与凭证中心

### 目标

建立运行期配置主数据，替代配置散落在 YAML、代码、前端和数据库字段中的状态。

### 开发内容

1. 配置定义表。
2. 配置版本表。
3. 配置发布表。
4. 配置绑定表。
5. 凭证表。
6. 凭证加密。
7. 凭证绑定。
8. 配置差异。
9. 配置回滚。
10. 配置漂移记录。
11. 配置影响范围分析。
12. 配置变更审计。

### 现有代码取舍

| 现有内容 | 判断 | 处理 |
|---|---|---|
| `config/*.yaml` | 可保留 | 作为默认模板，不作为运行期事实源 |
| `vendor_credentials.py` | 有价值 | 迁入 config/credential service |
| `api_keys.py` | 有价值 | 统一到凭证或 API Key 管理 |
| 前端 system/config 页面 | 有价值 | 改造成配置中心入口 |
| 散落在业务表中的配置字段 | 技术债 | 逐步迁移为配置绑定 |

### API 建议

```text
GET    /api/v1/config/definitions
POST   /api/v1/config/definitions
POST   /api/v1/config/definitions/{id}/versions
POST   /api/v1/config/versions/{id}/release
POST   /api/v1/config/releases/{id}/rollback
GET    /api/v1/config/diff
GET    /api/v1/config/impact
GET    /api/v1/config/drifts
POST   /api/v1/credentials
POST   /api/v1/credentials/{id}/test
POST   /api/v1/assets/{id}/credentials/{credential_id}/bind
```

### 验收标准

- 新增采集模板必须进入配置中心。
- 凭证不得明文存储。
- 配置变更必须有版本。
- 自动化执行记录必须保存所用配置版本。
- 配置发布可以回滚。

---

## 阶段 4：采集器运行时与状态中心

### 目标

把现有多采集器方向统一成标准采集器框架，采集结果进入状态中心。

### 开发内容

1. BaseCollector 接口。
2. Collector Registry。
3. Collector Capability。
4. Collector Health。
5. Collection Job。
6. Collection Result。
7. Collection Log。
8. State Snapshot。
9. State Change。
10. 最新状态缓存。
11. WebSocket 状态推送。

### 现有代码取舍

| 现有内容 | 判断 | 处理 |
|---|---|---|
| SNMP/SSH/WMI/API/Syslog 等采集器目录 | 方向正确 | 按 BaseCollector 统一改造 |
| discovery 模块 | 有价值 | 接入资产发现与采集任务 |
| device_manager.py | 有价值但边界需调整 | 迁入 collector 或 asset service |
| 各采集器自定义输出 | 技术债 | 改为统一输出格式 |
| 采集错误散落日志 | 技术债 | 写入 collection_job_logs |

### BaseCollector

```python
class BaseCollector:
    def validate_config(self, config): ...
    def test_connection(self, target, credential): ...
    def collect(self, target, config, context): ...
    def parse(self, raw_result): ...
    def normalize(self, parsed_result): ...
```

### 验收标准

- 至少 SSH 磁盘采集器完成统一接口改造。
- 采集结果能写入状态中心。
- 采集失败能记录失败原因。
- 状态变化能生成事件。
- 前端能看到最新状态和采集状态。

---

## 阶段 5：事件与告警中心

### 目标

从简单阈值告警升级为事件驱动架构。

### 开发内容

1. Event 模型。
2. Event Normalizer。
3. Event Correlator。
4. Event Rule。
5. Alert Rule。
6. Alert Lifecycle。
7. Alert Suppression。
8. Alert Escalation。
9. Alert Timeline。
10. Alert 与 Event、Asset、Log、Execution 关联。

### 现有代码取舍

| 现有内容 | 判断 | 处理 |
|---|---|---|
| monitoring/alerter | 有价值 | 拆分为 event detector 和 alert service |
| notification 触发逻辑 | 有价值 | 后续由 policy engine 调用 |
| workorder 自动生成逻辑 | 有价值 | 改为策略动作 |
| 简单阈值规则 | 保留 | 作为 alert rule 的一种 |
| 无生命周期的告警记录 | 重构 | 增加确认、处理中、关闭、复盘 |

### 验收标准

- 磁盘异常能先生成事件，再生成告警。
- 告警有生命周期。
- 告警详情能展示事件时间线。
- 告警能触发策略。
- 告警关闭必须有原因和验证结果。

---

## 阶段 6：日志与可观测中心

### 目标

把日志从“查询功能”升级为自动化闭环证据中心。

### 开发内容

1. 执行日志模型。
2. 执行日志分片。
3. stdout/stderr 实时流。
4. WebSocket 日志推送。
5. 采集日志。
6. 设备日志接入。
7. 审计日志。
8. 日志与告警关联。
9. 日志与工单关联。
10. AI 日志解释接口。

### 现有代码取舍

| 现有内容 | 判断 | 处理 |
|---|---|---|
| `log_service.py` | 有价值 | 升级为 log domain |
| `log_collector` | 有价值 | 接入日志中心 |
| `syslog_collector` | 有价值 | 统一输出格式 |
| 平台日志查询页面 | 可保留 | 改为日志中心页面的一部分 |
| 无 execution_id 的执行输出 | 重构 | 必须绑定 execution_id |

### 验收标准

- 自动化执行能实时看到日志。
- 日志按 execution_id 聚合。
- 执行失败可以看到 stderr。
- 告警详情能引用相关日志。
- AI 可以读取相关日志上下文。

---

## 阶段 7：策略中心

### 目标

把分散在告警、通知、工单、自动化中的规则统一为策略中心。

### 开发内容

1. Policy 模型。
2. Policy Version。
3. Policy Trigger。
4. Policy Scope。
5. Policy Condition。
6. Policy Action。
7. Policy Risk。
8. Policy Approval。
9. Policy Simulation。
10. Policy Conflict Detection。
11. Policy Hit Explanation。

### 现有代码取舍

| 现有内容 | 判断 | 处理 |
|---|---|---|
| 告警规则 | 保留 | 纳入策略触发源 |
| 通知规则 | 适配 | 作为策略动作 |
| 自动化触发规则 | 重构 | 由策略中心统一判断 |
| 工单派发规则 | 适配 | 作为策略动作 |
| 零散 if-else 规则 | 技术债 | 逐步迁移 |

### 验收标准

- 磁盘异常能命中策略。
- 前端能看到策略为什么命中。
- 策略能模拟。
- 策略能判断风险和审批要求。
- 策略冲突能被识别。

---

## 阶段 8：自动化执行中心

### 目标

建立安全可控的自动化执行引擎。

### 开发内容

1. 脚本库。
2. 脚本版本。
3. Playbook。
4. 执行任务。
5. 执行步骤。
6. 风险评估。
7. dry-run。
8. 审批。
9. 并发锁。
10. 实时日志。
11. 重试。
12. 回滚。
13. 后置验证。
14. 执行复盘。

### 现有代码取舍

| 现有内容 | 判断 | 处理 |
|---|---|---|
| `automation.py` | 有价值 | 迁入 automation domain |
| `modules/business/automation` | 有价值 | 拆分 script/playbook/execution |
| `auto_trigger_log.py` | 不确定 | 若是临时脚本则归档；有可复用逻辑则迁入 worker |
| 定时任务 | 保留 | 作为触发源之一 |
| 简单脚本执行 | 重构 | 增加状态机、日志、审批、验证、回滚 |

### 验收标准

- 每次执行有 execution_id。
- 每次执行有 step。
- 每个 step 有日志。
- 支持 dry-run。
- 支持风险判断。
- 支持审批。
- 支持验证。
- 失败能升级工单或回滚。

---

## 阶段 9：AIops 最小能力

### 目标

让 AI 进入故障闭环，而不是只做聊天。

### 开发内容

1. Context Builder。
2. Root Cause Analyzer。
3. Remediation Planner。
4. Log Interpreter。
5. Knowledge Draft Writer。
6. AI Feedback。
7. AI Tool Guard。

### 现有代码取舍

| 现有内容 | 判断 | 处理 |
|---|---|---|
| `ai.py` | 有价值 | 作为 aiops API 入口 |
| ai_copilot | 有价值 | 从聊天助手改为故障分析助手 |
| knowledge_base | 有价值 | 接入 RAG 和案例沉淀 |
| 纯聊天接口 | 降级 | 作为辅助入口，不是核心 |
| 无结构化输出 | 重构 | 必须输出 JSON 结构 |

### 验收标准

- AI 分析输入包含资产、指标、日志、事件、执行历史。
- AI 输出有证据、置信度、推荐动作。
- AI 不直接执行高危动作。
- 用户能反馈 AI 分析是否正确。
- AI 分析结果能进入工单或知识草稿。

---

## 阶段 10：前端工作流重构

### 目标

前端按运维流程重建，而不是后端模块堆页面。

### 新前端结构

```text
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
```

### 页面迁移

| 旧页面类型 | 新位置 | 处理 |
|---|---|---|
| 资产页面 | 资产与配置台 | 保留核心组件，重构详情页 |
| 监控页面 | 监控与事件台 | 拆分指标、状态、事件 |
| 告警页面 | 故障处置台入口 | 告警详情升级为处置页面 |
| 自动化页面 | 自动化编排台 | 增加策略、dry-run、日志、审批 |
| AI 页面 | AI 分析面板 + 知识问答 | 不再作为孤立聊天页 |
| 系统配置页面 | 平台管理台 + 配置中心 | 拆分运行配置和平台配置 |

### 验收标准

- 故障处置台能展示完整时间线。
- 执行控制台能实时显示日志。
- 配置发布台能展示差异和影响范围。
- 策略模拟台能展示命中解释。
- 用户在每个关键页面都知道下一步动作。

---

## 阶段 11：工单与知识闭环

### 目标

让工单和知识真正进入自动化闭环。

### 开发内容

1. 告警转工单。
2. 自动化失败转工单。
3. 策略触发工单。
4. 工单关联日志。
5. 工单关联执行。
6. 工单关联 AI 分析。
7. 工单关闭复盘。
8. 工单转知识。
9. 知识审核。
10. 相似案例推荐。

### 现有代码取舍

| 现有内容 | 判断 | 处理 |
|---|---|---|
| workorder 模块 | 有价值 | 接入事件、告警、执行 |
| knowledge_base | 有价值 | 升级为知识中心 |
| report 模块 | 可保留 | 后续用于复盘报告 |
| 单纯工单 CRUD | 重构 | 增加时间线和关联对象 |

### 验收标准

- 告警和执行失败可以自动生成工单。
- 工单能看到相关日志和执行记录。
- 工单关闭时能生成知识草稿。
- 知识可被 AI 检索。

---

## 4. 现有代码整体取舍清单

> 以下为原则性清单。实际执行时应在仓库中生成 `CODE_INVENTORY.md`，逐文件确认。

### 4.1 应保留的方向

- FastAPI 后端技术栈。
- Vue 3 前端技术栈。
- 本地化部署方向。
- 设备发现。
- 多协议采集方向。
- 资产纳管。
- 监控告警。
- 工单。
- 通知。
- 自动化任务。
- 日志采集。
- AI / 本地 LLM。
- 知识库。
- 报表。
- 系统管理。
- 备份恢复。

### 4.2 应适配的代码

| 代码类型 | 适配方式 |
|---|---|
| 资产 CRUD | 统一到 asset service |
| device API | 作为 asset 兼容层 |
| discovery API | 接入 discovery task 和 asset import |
| monitoring API | 拆到 state/event/alert |
| notification API | 变成 policy action |
| workorder API | 接入 alert/execution/ticket timeline |
| ai API | 升级为 aiops |
| log API | 升级为 log center |
| automation API | 升级为 automation engine |
| system config | 拆成 platform admin 和 config center |

### 4.3 应重构的代码

1. 路由中包含复杂业务逻辑的代码。
2. asset/device 重复模型。
3. 采集器输出格式不统一的代码。
4. 自动化执行没有状态机和日志的代码。
5. 告警没有生命周期的代码。
6. AI 只做自由问答的代码。
7. 配置散落在 YAML 和业务字段中的代码。
8. 前端按接口堆页面的代码。
9. 无统一错误码的接口。
10. 无 trace_id 和审计的关键操作。

### 4.4 应删除或归档的代码/文件

1. 本地数据库文件。
2. 临时测试脚本。
3. 未被引用的旧 demo。
4. 与现目标冲突的旧需求文档。
5. 重复 API。
6. 已废弃 TODO。
7. 自动生成但未维护的旧接口文档。
8. 没有维护价值的历史计划。
9. 旧截图、旧图表、旧状态报告。
10. 与平台目标无关的实验代码。

---

## 5. 文档治理方案

## 5.1 文档目录结构

```text
docs/
  00-overview/
    README.md
    PRODUCT_POSITIONING.md
    ROADMAP.md

  01-architecture/
    AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md
    BACKEND_ARCHITECTURE.md
    FRONTEND_ARCHITECTURE.md
    DATA_ARCHITECTURE.md
    EVENT_DRIVEN_ARCHITECTURE.md
    SECURITY_ARCHITECTURE.md

  02-domains/
    ASSET_CENTER.md
    CONFIG_CENTER.md
    COLLECTOR_AND_STATE_CENTER.md
    EVENT_ALERT_CENTER.md
    LOG_OBSERVABILITY_CENTER.md
    POLICY_ENGINE.md
    AUTOMATION_ENGINE.md
    AIOPS_KNOWLEDGE_CENTER.md
    TICKET_CENTER.md
    GOVERNANCE_CENTER.md

  03-api/
    API_CONTRACT.md
    ERROR_CODES.md
    AUTH_AND_PERMISSION.md
    WEBSOCKET_EVENTS.md

  04-frontend/
    UX_WORKFLOWS.md
    PAGE_STRUCTURE.md
    COMPONENT_GUIDE.md
    INCIDENT_RESPONSE_UI.md

  05-implementation/
    DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md
    PHASE_1_BACKEND_REFACTOR.md
    PHASE_2_INCIDENT_MVP.md
    CODE_INVENTORY.md
    API_INVENTORY.md
    FRONTEND_PAGE_INVENTORY.md
    TESTING_STRATEGY.md
    ACCEPTANCE_CRITERIA.md

  06-operations/
    DEPLOYMENT.md
    BACKUP_RESTORE.md
    OBSERVABILITY.md
    SECURITY.md
    PLATFORM_SELF_CHECK.md

  99-archive/
    old-requirements/
    old-designs/
    old-status/
    old-plans/
```

## 5.2 根目录治理

根目录只建议保留：

```text
README.md
CHANGELOG.md
LICENSE
.env.example
docker-compose.yml
Makefile
package files
startup scripts
```

不应继续放：

- 需求总表。
- 长篇设计文档。
- 临时分析文档。
- 实施状态杂文档。
- 旧计划。
- 本地数据库。
- 旧截图。
- 旧 demo 说明。

## 5.3 单一事实源

| 内容 | 唯一事实源 |
|---|---|
| 产品定位 | `docs/00-overview/PRODUCT_POSITIONING.md` |
| 总体架构 | `docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md` |
| 后端架构 | `docs/01-architecture/BACKEND_ARCHITECTURE.md` |
| 前端架构 | `docs/01-architecture/FRONTEND_ARCHITECTURE.md` |
| 数据架构 | `docs/01-architecture/DATA_ARCHITECTURE.md` |
| 领域设计 | `docs/02-domains/*.md` |
| API 规范 | `docs/03-api/API_CONTRACT.md` |
| 错误码 | `docs/03-api/ERROR_CODES.md` |
| 前端流程 | `docs/04-frontend/UX_WORKFLOWS.md` |
| 开发计划 | `docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md` |
| 部署运维 | `docs/06-operations/DEPLOYMENT.md` |

README 只作为入口，不承载详细设计。

## 5.4 文档状态标识

每个文档顶部必须包含：

```text
文档状态：current / draft / deprecated / archived
适用版本：
最后更新：
维护人：
对应模块：
是否为事实源：yes/no
替代文档：
```

## 5.5 文档更新规则

任何 PR 涉及以下内容，必须同步更新文档：

- 新增或修改领域模型。
- 新增或修改 API。
- 新增或修改数据库表。
- 新增或修改配置项。
- 新增或修改采集器。
- 新增或修改事件类型。
- 新增或修改策略。
- 新增或修改自动化动作。
- 新增或修改执行安全边界。
- 新增或修改前端页面。
- 新增或修改权限。
- 新增或修改部署方式。

## 5.6 PR 检查清单

每个 PR 必须回答：

```text
[ ] 是否修改 API？如是，是否更新 API_CONTRACT.md？
[ ] 是否修改数据库？如是，是否更新 DATA_ARCHITECTURE.md 或领域文档？
[ ] 是否新增配置？如是，是否更新 CONFIG_CENTER.md？
[ ] 是否新增事件？如是，是否更新 EVENT_ALERT_CENTER.md？
[ ] 是否新增策略？如是，是否更新 POLICY_ENGINE.md？
[ ] 是否新增自动化动作？如是，是否更新 AUTOMATION_ENGINE.md？
[ ] 是否修改前端页面？如是，是否更新 PAGE_STRUCTURE.md？
[ ] 是否影响部署？如是，是否更新 DEPLOYMENT.md？
[ ] 是否有过期文档需要归档？
```

## 5.7 归档规则

1. 过期文档不得删除历史，先移入 `docs/99-archive/`。
2. 归档文档顶部必须写明当前替代文档。
3. README 不得引用归档文档。
4. 归档文档不再作为开发依据。
5. 超过 30 天未更新且与代码不一致的 draft，应重新评审。
6. 与当前架构冲突的文档必须标记 deprecated 或 archived。

---

## 6. 立即可执行的仓库整理命令建议

### 6.1 新建目录

```bash
mkdir -p docs/00-overview
mkdir -p docs/01-architecture
mkdir -p docs/02-domains
mkdir -p docs/03-api
mkdir -p docs/04-frontend
mkdir -p docs/05-implementation
mkdir -p docs/06-operations
mkdir -p docs/99-archive/old-requirements
mkdir -p docs/99-archive/old-designs
mkdir -p docs/99-archive/old-status
mkdir -p docs/99-archive/old-plans
```

### 6.2 迁移旧文档

根据当前仓库实际文件名执行。原则如下：

```bash
git mv REQUIREMENTS_MASTER.md docs/99-archive/old-requirements/
git mv TODO.md docs/99-archive/old-plans/
git mv DESIGN.md docs/99-archive/old-designs/DESIGN.old.md
git mv SPEC.md docs/99-archive/old-designs/SPEC.old.md
git mv IMPLEMENTATION_STATUS.md docs/99-archive/old-status/IMPLEMENTATION_STATUS.old.md
```

### 6.3 删除本地数据库文件

```bash
git rm --cached itops_platform.db
echo "*.db" >> .gitignore
echo "itops_platform.db" >> .gitignore
```

### 6.4 新增当前事实源文档

```text
docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md
docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md
```

---

## 7. MVP 开发任务拆解

## 7.1 MVP 名称

Linux 磁盘空间异常自动处置闭环。

## 7.2 MVP 范围

必须包含：

1. Linux 资产。
2. SSH 凭证。
3. 磁盘采集模板。
4. 磁盘指标采集。
5. 状态中心。
6. 事件中心。
7. 告警中心。
8. AI 分析。
9. 策略命中。
10. dry-run。
11. 自动化执行。
12. 实时日志。
13. 结果验证。
14. 工单升级。
15. 知识草稿。

## 7.3 MVP 不做的内容

第一版可以暂不做：

- 多租户。
- 复杂拖拽编排。
- 全部设备类型。
- 全量报表。
- 插件市场。
- 大规模高可用。
- 所有外部系统集成。
- 全部 AI 工具调用。

## 7.4 MVP 任务列表

### 后端

| 编号 | 任务 | 模块 |
|---|---|---|
| B1 | 建立 asset 统一模型 | asset |
| B2 | 建立 SSH credential 模型 | config |
| B3 | 建立 disk collection profile | config |
| B4 | 实现 SSH disk collector | collector |
| B5 | 写入 metric/state | state |
| B6 | 状态变化生成事件 | event |
| B7 | 事件生成告警 | alert |
| B8 | 告警详情聚合上下文 | alert/aiops |
| B9 | AI 结构化分析 | aiops |
| B10 | 磁盘清理策略 | policy |
| B11 | dry-run | automation |
| B12 | 执行清理脚本 | automation |
| B13 | 实时日志 WebSocket | log |
| B14 | 执行后重新采集验证 | collector/state |
| B15 | 失败转工单 | ticket |
| B16 | 成功生成知识草稿 | knowledge |

### 前端

| 编号 | 任务 | 页面 |
|---|---|---|
| F1 | 资产列表和资产详情 | 资产与配置台 |
| F2 | 凭证绑定 | 资产与配置台 |
| F3 | 采集模板绑定 | 资产与配置台 |
| F4 | 磁盘指标趋势 | 监控与事件台 |
| F5 | 告警列表 | 监控与事件台 |
| F6 | 告警详情 | 故障处置台 |
| F7 | AI 分析面板 | 故障处置台 |
| F8 | 推荐动作面板 | 故障处置台 |
| F9 | dry-run 结果 | 自动化执行控制台 |
| F10 | 实时日志窗口 | 自动化执行控制台 |
| F11 | 验证结果 | 故障处置台 |
| F12 | 工单升级入口 | 故障处置台 |
| F13 | 知识草稿入口 | AI 与知识台 |

## 7.5 MVP 验收标准

1. 不能只造假数据，必须有真实或可重复模拟的采集器。
2. 不能只返回 success，必须有 step 级日志。
3. 不能只执行脚本，必须有风险判断和 dry-run。
4. 不能只发通知，必须有告警生命周期。
5. AI 不能只输出自然语言，必须结构化输出。
6. 告警详情必须展示完整证据链。
7. 自动化执行必须有实时日志。
8. 执行后必须重新采集验证。
9. 成功关闭告警必须有验证依据。
10. 失败必须能转工单。
11. 工单或执行记录必须能生成知识草稿。
12. 全链路必须有 trace_id。

---

## 8. 测试策略

### 8.1 单元测试

覆盖：

- 资产 service。
- 配置版本。
- 采集器 normalize。
- 状态变更判断。
- 事件生成。
- 告警规则。
- 策略命中。
- 风险判断。
- dry-run。
- 执行状态机。
- AI 输出解析。

### 8.2 集成测试

覆盖：

- 资产 → 配置绑定。
- 配置 → 采集任务。
- 采集 → 状态。
- 状态 → 事件。
- 事件 → 告警。
- 告警 → 策略。
- 策略 → 自动化执行。
- 执行 → 日志。
- 执行 → 验证。
- 失败 → 工单。

### 8.3 前端 E2E

覆盖：

- 新建资产。
- 绑定凭证。
- 触发采集。
- 查看状态。
- 查看告警。
- 查看 AI 分析。
- 执行 dry-run。
- 执行自动化。
- 查看实时日志。
- 查看验证结果。

---

## 9. 里程碑建议

### M1：仓库治理完成

产出：

- 文档目录重建。
- 旧文档归档。
- 新架构文档上线。
- 代码清单完成。

### M2：后端主干完成

产出：

- 领域目录。
- asset/config/collector/state/event/alert 基础能力。
- 统一响应、错误码、trace_id。

### M3：MVP 后端闭环完成

产出：

- Linux 磁盘采集。
- 告警。
- 策略。
- 自动化。
- 实时日志。
- 验证。

### M4：MVP 前端闭环完成

产出：

- 资产与配置台。
- 告警详情。
- 故障处置台。
- 实时日志控制台。

### M5：AI 与知识闭环完成

产出：

- AI 结构化分析。
- 工单转知识。
- 执行转知识。
- 用户反馈。

### M6：扩展场景

扩展：

- 服务不可用自动重启。
- 端口不可达诊断。
- CPU 异常分析。
- 证书过期。
- 数据库连接异常。
- 备份失败处理。

---

## 10. 最终执行建议

下一步不要再继续“泛泛扩功能”，而应按以下顺序执行：

1. 把完整架构文档和本开发治理方案放入 docs。
2. 归档旧文档，清理根目录。
3. 建立领域目录。
4. 合并 asset/device。
5. 建立配置中心。
6. 改造一个 SSH 磁盘采集器。
7. 建立状态、事件、告警链路。
8. 建立策略和自动化执行状态机。
9. 建立实时日志。
10. 建立故障处置台。
11. 用磁盘异常场景验收全链路。
12. 再扩展其他场景。

只要这个主干跑通，后续新增设备类型、采集协议、告警规则、自动化剧本、AI 分析能力，都会变成在稳定平台底座上的扩展，而不是继续制造新的技术债。

---

# 附加融合内容：来自上传建议的开发治理补强

## A. 客观采纳结论

上传建议中对开发计划和治理机制有较多可借鉴内容，尤其适合补强工程化、私有化交付、安全和质量保障。但其中部分能力应延后，不能压到第一阶段。

### A.1 融入本最终开发计划的内容

1. Docs as Code。
2. docs-check CI。
3. OpenAPI 自动导出。
4. ADR 架构决策记录。
5. pre-commit、ruff、black。
6. pytest。
7. testcontainers-python。
8. Playwright/Cypress。
9. DevSecOps 安全检查。
10. OpenTelemetry。
11. 凭证 AES-256-GCM 加密。
12. 高危自动化动作 MFA 或二次确认。
13. 离线部署包。
14. install.sh、upgrade.sh、rollback.sh。
15. Alembic migration。
16. 本地模型部署说明。
17. LangGraph 作为 AI Agent 中后期演进方向。

### A.2 不直接进入第一阶段的内容

1. eBPF。
2. FinOps。
3. 多活高可用。
4. 完整低代码工单引擎。
5. 完全自主 AI Agent。
6. 复杂知识图谱。

这些能力可以列入 P2/P3，不应影响当前主干闭环重构。

---

## B. 文档治理升级为 Docs as Code

### B.1 文档目录最终建议

```text
docs/
  00-overview/
    README.md
    PRODUCT_POSITIONING.md
    ROADMAP.md

  01-architecture/
    AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md
    BACKEND_ARCHITECTURE.md
    FRONTEND_ARCHITECTURE.md
    DATA_ARCHITECTURE.md
    EVENT_DRIVEN_ARCHITECTURE.md
    SECURITY_ARCHITECTURE.md
    adr/
      ADR-0001-docs-as-code.md
      ADR-0002-domain-architecture.md

  02-domains/
    ASSET_CENTER.md
    CONFIG_CENTER.md
    COLLECTOR_AND_STATE_CENTER.md
    EVENT_ALERT_CENTER.md
    LOG_OBSERVABILITY_CENTER.md
    POLICY_ENGINE.md
    AUTOMATION_ENGINE.md
    AIOPS_KNOWLEDGE_CENTER.md
    TICKET_CENTER.md
    GOVERNANCE_CENTER.md

  03-api/
    API_CONTRACT.md
    ERROR_CODES.md
    AUTH_AND_PERMISSION.md
    WEBSOCKET_EVENTS.md
    openapi.json

  04-frontend/
    UX_WORKFLOWS.md
    PAGE_STRUCTURE.md
    COMPONENT_GUIDE.md
    INCIDENT_RESPONSE_UI.md

  05-implementation/
    DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md
    PHASE_1_BACKEND_REFACTOR.md
    PHASE_2_INCIDENT_MVP.md
    CODE_INVENTORY.md
    API_INVENTORY.md
    FRONTEND_PAGE_INVENTORY.md
    TESTING_STRATEGY.md
    ACCEPTANCE_CRITERIA.md

  06-operations/
    DEPLOYMENT.md
    OFFLINE_DEPLOYMENT.md
    UPGRADE_AND_ROLLBACK.md
    BACKUP_RESTORE.md
    OBSERVABILITY.md
    SECURITY.md
    PLATFORM_SELF_CHECK.md

  07-development/
    CONTRIBUTING.md
    PR_CHECKLIST.md
    TESTING_GUIDE.md
    CODING_STYLE.md

  99-archive/
    old-requirements/
    old-designs/
    old-status/
    old-plans/
```

### B.2 docs-check CI 规则

建议在 GitHub Actions 中实现：

- 修改 `backend/api/`，必须更新 `docs/03-api/` 或生成新的 `openapi.json`。
- 修改 `backend/app/domains/asset/`，必须更新 `docs/02-domains/ASSET_CENTER.md`。
- 修改 `backend/app/domains/config/`，必须更新 `docs/02-domains/CONFIG_CENTER.md`。
- 修改 `backend/app/domains/automation/`，必须更新 `docs/02-domains/AUTOMATION_ENGINE.md`。
- 修改 `backend/app/domains/aiops/`，必须更新 `docs/02-domains/AIOPS_KNOWLEDGE_CENTER.md`。
- 修改 `frontend/src/features/`，必须更新 `docs/04-frontend/`。
- 修改 `docker-compose.yml`、部署脚本或环境变量，必须更新 `docs/06-operations/`。
- 修改安全、权限、凭证、脱敏相关代码，必须更新 `SECURITY_ARCHITECTURE.md`。

### B.3 OpenAPI 自动化

API 文档不再手工维护。建议流程：

1. FastAPI 自动生成 OpenAPI schema。
2. CI 或 release 阶段导出 `openapi.json`。
3. 将 `openapi.json` 保存到 `docs/03-api/openapi.json`。
4. 可选：生成静态 HTML API 页面。
5. README 只链接 API 文档，不手写接口详情。

### B.4 ADR 机制

所有重大技术决策必须记录 ADR，包括：

- 数据库选择。
- 消息队列选择。
- 时序库选择。
- 日志库选择。
- 向量库选择。
- AI Agent 框架选择。
- 自动化执行安全边界。
- 多租户隔离方式。
- 离线部署方式。
- 高可用方案。

ADR 模板：

```text
# ADR-编号-标题

## 状态
proposed / accepted / deprecated / superseded

## 背景

## 决策

## 备选方案

## 影响

## 后续动作
```

---

## C. 开发阶段补强

## 阶段 0 补强：仓库治理与基础质量

在原阶段 0 基础上新增：

1. 增加 `.pre-commit-config.yaml`。
2. 增加 ruff。
3. 增加 black。
4. 增加 pytest 基础目录。
5. 增加 docs-check GitHub Action。
6. 增加 OpenAPI 自动导出脚本。
7. 增加 ADR 目录。
8. 增加 Secret 扫描。
9. 增加依赖漏洞扫描。
10. 增加基础 CI。

新增交付物：

```text
.pre-commit-config.yaml
.github/workflows/ci.yml
.github/workflows/docs-check.yml
scripts/export_openapi.py
docs/01-architecture/adr/
docs/07-development/CONTRIBUTING.md
docs/07-development/TESTING_GUIDE.md
```

---

## 阶段 1 补强：统一基础设施

在原阶段 1 基础上新增：

1. OpenTelemetry 基础埋点。
2. API 统一审计中间件。
3. 动态脱敏工具。
4. 凭证加密工具。
5. API Key 权限范围控制。
6. Secret 配置检查。
7. 平台组件健康检查接口。

新增验收标准：

- 每次请求有 trace_id。
- 关键 API 有审计日志。
- 敏感字段可脱敏输出。
- 凭证加密工具可用。
- 平台健康检查接口可用。
- API/Worker 基础 trace 可用。

---

## 阶段 3 补强：配置与凭证中心

新增工作项：

1. 凭证 AES-256-GCM 加密。
2. 密钥来源检查。
3. 凭证使用审计。
4. 凭证测试连接。
5. 动态脱敏规则。
6. 高危配置变更审批。
7. 配置变更 ADR/Change Record 关联。

新增验收标准：

- 凭证不得明文落库。
- 导出数据不得包含明文凭证。
- AI 不得读取明文凭证。
- 凭证使用必须记录审计日志。
- 高危配置变更可审批。

---

## 阶段 6 补强：日志与可观测中心

新增工作项：

1. FastAPI OTel trace。
2. Worker 任务 trace。
3. 数据库查询耗时。
4. 队列积压指标。
5. WebSocket 连接数。
6. AI 调用耗时。
7. 自动化执行链路 trace。
8. 平台自身健康看板。

新增验收标准：

- API 延迟可观测。
- Worker 队列深度可观测。
- AI 调用耗时可观测。
- 自动化执行链路可追踪。
- 平台自身异常能产生平台告警。

---

## 阶段 8 补强：自动化执行安全

新增工作项：

1. 高危命令黑名单。
2. 危险命令熔断。
3. MFA 二次确认。
4. 自动执行白名单。
5. 生产环境执行限制。
6. 批量执行最大影响面控制。
7. Ansible Playbook 接入预留。
8. 执行脚本安全扫描。

新增验收标准：

- 高危命令能被阻断。
- 生产环境高危动作需要二次确认。
- 批量执行受最大影响面限制。
- 自动化执行必须有审计记录。
- 脚本版本和执行参数可追溯。

---

## 阶段 9 补强：AIops 与 Agentic Workflow

新增工作项：

1. 只读工具调用接口。
2. AI Tool Guard。
3. LangGraph 预研和接口预留。
4. Human-in-the-loop 确认机制。
5. AI 工具调用审计。
6. 历史工单解析。
7. 设备手册解析。
8. RAG 文档分块和向量化。

AI 分阶段：

| 阶段 | 能力 | 安全边界 |
|---|---|---|
| A1 | 结构化分析和推荐动作 | 不调用执行工具 |
| A2 | 只读工具调用 | 只读权限、全量审计 |
| A3 | 生成执行计划 | 必须由策略中心校验 |
| A4 | 低风险动作自动执行 | 仅限策略白名单 |
| A5 | 高风险动作执行 | 必须人工确认和审计 |

---

## 新增阶段 12：私有化部署与升级

### 目标

让平台支持真实客户现场部署、无外网部署、升级和回滚。

### 开发内容

1. 离线部署包。
2. Docker 镜像打包。
3. Python wheelhouse。
4. install.sh。
5. upgrade.sh。
6. rollback.sh。
7. Alembic migration。
8. 配置差异保留。
9. 升级前备份。
10. 升级后自检。
11. 本地模型部署说明。
12. Ollama/vLLM 启动检查。
13. 单机 Docker Compose 部署。
14. 后续多节点部署预留。

### 验收标准

- 无外网环境可以部署。
- 升级前自动备份。
- 升级后自动自检。
- 升级失败可以回滚。
- 平台自身状态可在前端查看。
- 模型服务不可用时平台能降级。

---

## D. 测试体系补强

### D.1 单元测试

使用 pytest，覆盖：

- 资产 service。
- 配置版本。
- 凭证加密和脱敏。
- 采集器 normalize。
- 状态变更判断。
- 事件生成。
- 告警规则。
- 策略命中。
- 风险判断。
- dry-run。
- 执行状态机。
- AI 输出解析。
- 权限校验。
- 数据脱敏。

核心业务逻辑测试覆盖率目标：80%+。

### D.2 集成测试

建议使用 testcontainers-python，在 CI 中拉起真实依赖：

- PostgreSQL/MySQL。
- Redis。
- RabbitMQ 或 Redis Streams。
- MinIO。
- 向量库可在后期加入。

覆盖：

- 资产 → 配置绑定。
- 配置 → 采集任务。
- 采集 → 状态。
- 状态 → 事件。
- 事件 → 告警。
- 告警 → 策略。
- 策略 → 自动化执行。
- 执行 → 日志。
- 执行 → 验证。
- 失败 → 工单。

### D.3 前端 E2E

使用 Playwright 或 Cypress，覆盖：

- 登录。
- 新建资产。
- 绑定凭证。
- 触发采集。
- 查看状态。
- 查看告警。
- 查看 AI 分析。
- 执行 dry-run。
- 执行自动化。
- 查看实时日志。
- 查看验证结果。

### D.4 安全测试

覆盖：

- Secret 扫描。
- 依赖漏洞扫描。
- 镜像漏洞扫描。
- 高危接口权限测试。
- 凭证明文泄露测试。
- 动态脱敏测试。
- 自动化高危命令阻断测试。
- API Key 越权测试。

### D.5 容错与混沌测试

第一阶段不需要引入复杂 Chaos Mesh，但应使用脚本模拟：

- Redis 不可用。
- 数据库连接延迟。
- 采集器离线。
- Worker 任务失败。
- WebSocket 断开。
- LLM 服务不可用。

验证平台是否能降级、告警和恢复。

---

## E. MVP 范围补强

MVP 原范围保留，同时新增企业级底线：

1. trace_id。
2. 凭证加密。
3. 审计日志。
4. 高危命令阻断。
5. 平台自身基础监控。
6. OpenAPI 自动导出。
7. pytest 覆盖关键 service。
8. docs-check CI。

MVP 不做：

- eBPF。
- FinOps。
- 多活高可用。
- 完整低代码工单引擎。
- 全自主 AI Agent。
- 复杂知识图谱。

---

## F. 里程碑补强

### M0：仓库治理完成

产出：

- 文档目录重建。
- 旧文档归档。
- 新架构文档上线。
- 代码清单完成。
- docs-check CI。
- pre-commit。
- ADR 目录。
- OpenAPI 自动导出脚本。

### M1：后端主干完成

产出：

- 领域目录。
- asset/config/collector/state/event/alert 基础能力。
- 统一响应、错误码、trace_id。
- 凭证加密。
- 审计日志。
- 基础 OTel。

### M2：MVP 后端闭环完成

产出：

- Linux 磁盘采集。
- 告警。
- 策略。
- 自动化。
- 实时日志。
- 验证。
- 工单。
- 知识草稿。

### M3：MVP 前端闭环完成

产出：

- 资产与配置台。
- 告警详情。
- 故障处置台。
- 实时日志控制台。
- 平台健康小组件。

### M4：AI 与知识闭环完成

产出：

- AI 结构化分析。
- 只读工具调用。
- 工单转知识。
- 执行转知识。
- 用户反馈。

### M5：私有化部署与自运维完成

产出：

- install.sh。
- upgrade.sh。
- rollback.sh。
- 离线部署包。
- 平台一键自检。
- 备份恢复。

### M6：扩展场景

扩展：

- 服务不可用自动重启。
- 端口不可达诊断。
- CPU 异常分析。
- 证书过期。
- 数据库连接异常。
- 备份失败处理。
- Agent 模式。
- 边缘采集器。

---

## G. 最终执行建议

下一步执行顺序调整为：

1. 放入最终版架构文档和本开发治理方案。
2. 归档旧文档，清理根目录。
3. 建立 Docs as Code、docs-check、ADR 和 OpenAPI 自动导出机制。
4. 建立 pre-commit、ruff、black、pytest。
5. 建立领域目录。
6. 合并 asset/device。
7. 建立配置中心和凭证加密。
8. 改造一个 SSH 磁盘采集器。
9. 建立状态、事件、告警链路。
10. 建立策略和自动化执行状态机。
11. 建立实时日志和审计。
12. 建立故障处置台。
13. 加入平台自身基础可观测。
14. 用磁盘异常场景验收全链路。
15. 建立离线部署和升级脚本。
16. 再扩展其他场景。
