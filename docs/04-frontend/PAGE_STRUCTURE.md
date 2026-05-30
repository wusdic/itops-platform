# ITOps Platform 页面结构

> 文档状态：current
> 版本：v1.0
> 事实源：代码扫描生成（`frontend/src/features/` + `frontend/src/views/`）
> 最后更新：2026-05-30

---

## 1. 整体结构

```
前端应用
├── /login                          登录页
├── /layout                         管理后台框架
│   ├── /dashboard                  仪表盘（首页）
│   ├── /command-center             运维指挥台（Phase 10 新建）
│   ├── /incident-response          故障处置台（Phase 10 新建）
│   ├── /automation-orchestration  自动化编排台（Phase 10 新建）
│   ├── /monitoring-event           监控与事件台（Phase 10 新建）
│   └── /asset-config              资产与配置台（Phase 10 新建）
└── /views/...                     旧页面（日常运维模块）
```

---

## 2. Phase 10 新建页面（`features/`）

> 这 5 个页面是核心运维闭环入口，按运维流程组织，每个页面 570~791 行。

| 路径 | 文件 | 行数 | 核心功能 |
|---|---|---|---|
| `/command-center` | `features/command-center/CommandCenterView.vue` | 579 | 严重告警排行、AI建议摘要、自动化任务状态、设备采集成功率 |
| `/incident-response` | `features/incident-response/IncidentResponseView.vue` | 570 | 告警时间线、证据分析Tab（事件/日志/资产）、AI分析、SSE实时日志 |
| `/automation-orchestration` | `features/automation-orchestration/AutomationOrchestrationView.vue` | 791 | 剧本库、任务管理、执行历史、审批中心 |
| `/monitoring-event` | `features/monitoring-event/MonitoringEventView.vue` | 612 | 指标监控、日志检索、事件流、告警中心、告警规则 |
| `/asset-config` | `features/asset-config/AssetConfigView.vue` | 640 | 资产列表、凭证管理、配置管理 |

### 2.1 运维指挥台 `/command-center`

**布局：**
- 顶部：系统状态摘要 + AI 建议卡片
- 左侧：严重告警列表（按级别排序）
- 中部：自动化任务状态面板
- 右侧：设备采集成功率图表

**核心交互：**
- 点击告警 → 跳转故障处置台
- 点击 AI 建议 → 展开推荐动作
- 点击自动化任务 → 跳转自动化编排台

### 2.2 故障处置台 `/incident-response`

**布局：**
- 左侧：告警时间线（垂直滚动）
- 右侧 Tab：证据分析（关联事件 / 关联日志 / 关联资产）
- 底部：AI 分析结果面板
- 右下角：SSE 实时日志窗口

**核心交互：**
- 选择告警 → 时间线自动展开
- AI 分析按钮 → 调用 `/api/v1/ai/analyze`
- 执行推荐动作 → 调用自动化编排台
- 关闭告警 → 沉淀知识

### 2.3 自动化编排台 `/automation-orchestration`

**布局：**
- 左侧：剧本库（分类列表）
- 右侧 Tab：任务管理 / 执行历史 / 审批中心
- 执行详情：SSE 实时日志流

**核心交互：**
- 选择剧本 → dry-run → 审批（如需）→ 执行
- SSE 实时日志 → 执行结果验证
- 审批通过/拒绝 → 触发自动化

### 2.4 监控与事件台 `/monitoring-event`

**布局：**
- Tab：指标监控 / 日志检索 / 事件流 / 告警中心 / 告警规则
- 指标 Tab：ECharts 图表 + 设备列表
- 事件流：实时滚动事件列表
- 告警规则：规则列表 + 规则编辑器

### 2.5 资产与配置台 `/asset-config`

**布局：**
- Tab：资产列表 / 凭证管理 / 配置管理
- 资产列表：el-table + 分页
- 凭证管理：凭证列表 + 绑定关系
- 配置管理：配置版本历史 + 发布/回滚

---

## 3. 旧页面（`views/`）

### 3.1 仪表盘 & 首页

| 路径 | 文件 | 说明 |
|---|---|---|
| `/dashboard` | `views/dashboard/index.vue` | 首页仪表盘 |
| `/systemHealth` | `views/systemHealth.vue` | 系统健康状态 |

### 3.2 监控（Monitoring）

| 路径 | 文件 | 说明 |
|---|---|---|
| `/monitoring/devices` | `views/monitoring/devices.vue` | 设备监控 |
| `/monitoring/alerts` | `views/monitoring/alerts.vue` | 告警管理 |
| `/monitoring/logs` | `views/monitoring/logs.vue` | 日志管理 |
| `/monitoring/dashboard` | `views/monitoring/dashboard.vue` | 监控仪表盘 |
| `/monitoring/triggers` | `views/monitoring/triggers.vue` | 触发器配置 |
| `/monitoring/performance` | `views/monitoring/performance.vue` | 性能监控 |
| `/monitoring/maintenance` | `views/monitoring/maintenance.vue` | 维护窗口 |

### 3.3 工单（Workorder）

| 路径 | 文件 | 说明 |
|---|---|---|
| `/workorder/list` | `views/workorder/list.vue` | 工单列表 |
| `/workorder/my` | `views/workorder/my.vue` | 我的工单 |
| `/workorder/create` | `views/workorder/create.vue` | 创建工单 |
| `/workorder/detail` | `views/workorder/detail.vue` | 工单详情 |

### 3.4 知识库（Knowledge）

| 路径 | 文件 | 说明 |
|---|---|---|
| `/knowledge/list` | `views/knowledge/list.vue` | 知识列表 |
| `/knowledge/category` | `views/knowledge/category.vue` | 知识分类 |
| `/knowledge/cases` | `views/knowledge/cases.vue` | 案例库 |

### 3.5 自动化（Automation）

| 路径 | 文件 | 说明 |
|---|---|---|
| `/automation/script` | `views/automation/script.vue` | 脚本管理 |
| `/automation/execute` | `views/automation/execute.vue` | 执行页面 |
| `/automation/task` | `views/automation/task.vue` | 任务管理 |
| `/automation/evaluate` | `views/automation/evaluate.vue` | 评估页面 |

### 3.6 系统管理（System）

| 路径 | 文件 | 说明 |
|---|---|---|
| `/system/user` | `views/system/user.vue` | 用户管理 |
| `/system/role` | `views/system/role.vue` | 角色管理 |
| `/system/menu` | `views/system/menu.vue` | 菜单管理 |
| `/system/dict` | `views/system/dict.vue` | 字典管理 |
| `/system/config` | `views/system/config.vue` | 系统配置 |
| `/system/logs` | `views/system/logs.vue` | 系统日志 |
| `/system/adapters` | `views/system/adapters.vue` | 适配器管理 |

### 3.7 AI

| 路径 | 文件 | 说明 |
|---|---|---|
| `/ai/chat` | `views/ai/chat.vue` | AI 聊天 |
| `/ai/copilot` | `views/ai/copilot.vue` | AI 副驾驶 |
| `/ai/analyze` | `views/ai/analyze.vue` | AI 分析 |

### 3.8 其他功能

| 路径 | 文件 | 说明 |
|---|---|---|
| `/discovery` | `views/discovery/index.vue` | 发现首页 |
| `/discovery/scan` | `views/discovery/scan.vue` | 扫描配置 |
| `/discovery/targets` | `views/discovery/targets.vue` | 扫描目标 |
| `/report/list` | `views/report/list.vue` | 报表列表 |
| `/report/create` | `views/report/create.vue` | 创建报表 |
| `/report/template` | `views/report/template.vue` | 报表模板 |
| `/backup/list` | `views/backup/list.vue` | 备份列表 |
| `/backup/restore` | `views/backup/restore.vue` | 恢复页面 |
| `/notification/message` | `views/notification/message.vue` | 消息中心 |
| `/notification/history` | `views/notification/history.vue` | 通知历史 |
| `/notification/config` | `views/notification/config.vue` | 通知配置 |
| `/api-keys` | `views/api-keys/index.vue` | API 密钥 |
| `/tenants` | `views/tenants/index.vue` | 租户管理 |
| `/ldap` | `views/ldap/index.vue` | LDAP 配置 |
| `/watermark` | `views/watermark/index.vue` | 水印管理 |
| `/deploy/health` | `views/deploy/health.vue` | 部署健康 |
| `/deploy/versions` | `views/deploy/versions.vue` | 版本管理 |
| `/deploy/canary` | `views/deploy/canary.vue` | 金丝雀发布 |
| `/inspection/tasks` | `views/inspection/tasks.vue` | 巡检任务 |
| `/inspection/report` | `views/inspection/report.vue` | 巡检报告 |
| `/management/VendorCredentials` | `views/management/VendorCredentials.vue` | 厂商凭证 |
| `/sharding` | `views/sharding/index.vue` | 分片管理 |

---

## 4. 路由配置

路由定义在 `frontend/src/router/index.js`，主要结构：

```javascript
{
  path: '/login',
  component: () => import('@/views/login/index.vue')
},
{
  path: '/',
  component: () => import('@/views/layout/index.vue'),
  children: [
    { path: 'dashboard', component: () => import('@/views/dashboard/index.vue') },
    { path: 'command-center', component: () => import('@/features/command-center/CommandCenterView.vue') },
    { path: 'incident-response', component: () => import('@/features/incident-response/IncidentResponseView.vue') },
    { path: 'automation-orchestration', component: () => import('@/features/automation-orchestration/AutomationOrchestrationView.vue') },
    { path: 'monitoring-event', component: () => import('@/features/monitoring-event/MonitoringEventView.vue') },
    { path: 'asset-config', component: () => import('@/features/asset-config/AssetConfigView.vue') },
    // ... 旧页面路由
  ]
}
```

---

## 5. API 路由对照

| 前端页面 | 主要 API 路径 |
|---|---|
| 运维指挥台 | `/api/v1/alerts`, `/api/v1/events`, `/api/v1/automation/executions` |
| 故障处置台 | `/api/v1/alerts/{id}/evidence`, `/api/v1/ai/analyze`, `/api/v1/events` |
| 自动化编排台 | `/api/v1/automation/scripts`, `/api/v1/automation/executions` |
| 监控与事件台 | `/api/v1/monitoring/alerts`, `/api/v1/events`, `/api/v1/logs` |
| 资产与配置台 | `/api/v1/assets`, `/api/v1/configs`, `/api/v1/collectors` |
| 工单 | `/api/v1/workorders` |
| 知识库 | `/api/v1/knowledge/articles` |
| 系统管理 | `/api/v1/users`, `/api/v1/system`, `/api/v1/config` |

---

## 6. 组件库使用

- **Phase 10 新页面**：Element Plus（`el-button`, `el-table`, `el-pagination`, `el-tab` 等）
- **旧页面**：Element Plus + Naive UI 混用
- **图表**：ECharts（`MonitoringEventView.vue` 等）
- **图标**：Element Plus 内置图标
