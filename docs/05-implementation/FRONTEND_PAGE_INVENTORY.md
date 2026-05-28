# 前端页面清单

> 文档状态：current
> 适用版本：v2.0
> 最后更新：2026-05-28
> 维护人：ITOPS 开发团队
> 是否为事实源：yes

---

## 说明

本文档记录所有前端页面，按目标架构的工作台组织。处理状态：
- **keep**：保留，核心功能
- **adapt**：需适配到新工作台结构
- **refactor**：需重构页面结构和交互
- **remove**：孤立页面/临时页面，应删除
- **archive**：已归档组件，不再使用

---

## 1. 运维指挥台 (Command Center)

| 页面路径 | 功能 | 状态 | 说明 |
|----------|------|------|------|
| `views/dashboard/index.vue` | 主仪表盘 | adapt | 需升级为运维指挥台，展示故障概览、自动化状态、AI建议 |
| `views/systemHealth.vue` | 系统健康 | adapt | 纳入运维指挥台或平台自检 |

---

## 2. 资产与配置台 (Asset & Config)

| 页面路径 | 功能 | 状态 | 说明 |
|----------|------|------|------|
| `views/discovery/index.vue` | 资产发现 | keep | 资产发现入口 |
| `views/discovery/scan.vue` | 扫描配置 | keep | 扫描任务 |
| `views/discovery/targets.vue` | 发现目标 | keep | 发现结果确认 |
| `views/monitoring/devices.vue` | 设备列表 | adapt | 改为资产列表 |
| `views/management/VendorCredentials.vue` | 厂商凭证 | adapt | 升级为统一凭证中心 |

---

## 3. 监控与事件台 (Monitoring & Event)

| 页面路径 | 功能 | 状态 | 说明 |
|----------|------|------|------|
| `views/monitoring/alerts.vue` | 告警列表 | adapt | 升级为告警中心，含生命周期管理 |
| `views/monitoring/dashboard.vue` | 监控仪表盘 | adapt | 改为监控与事件台 |
| `views/monitoring/performance.vue` | 性能监控 | adapt | 指标监控 |
| `views/monitoring/triggers.vue` | 告警规则 | adapt | 升级为告警规则管理 |
| `views/monitoring/maintenance.vue` | 维护窗口 | keep | 维护窗口管理 |
| `views/notification/config.vue` | 通知配置 | adapt | 改为策略动作配置 |
| `views/notification/history.vue` | 通知历史 | adapt | 纳入告警时间线 |
| `views/notification/message.vue` | 消息中心 | adapt | 纳入通知中心 |

---

## 4. 故障处置台 (Incident Response)

| 页面路径 | 功能 | 状态 | 说明 |
|----------|------|------|------|
| `views/monitoring/alerts.vue` (详情) | 告警详情 | refactor | 升级为完整故障处置台：左侧时间线+中间证据+右侧动作+底部日志 |
| `views/ai/analyze.vue` | AI 分析 | adapt | 纳入故障处置台作为分析面板 |
| `views/ai/copilot.vue` | AI 助手 | adapt | 改为故障分析助手，不再是独立聊天页 |

---

## 5. 自动化编排台 (Automation Orchestration)

| 页面路径 | 功能 | 状态 | 说明 |
|----------|------|------|------|
| `views/automation/script.vue` | 脚本库 | keep | |
| `views/automation/execute.vue` | 执行控制台 | refactor | 需增加实时日志、dry-run、审批状态 |
| `views/automation/task.vue` | 任务管理 | adapt | |
| `views/automation/evaluate.vue` | 风险评估 | adapt | 改为策略编排的一部分 |

---

## 6. AI 与知识台 (AI & Knowledge)

| 页面路径 | 功能 | 状态 | 说明 |
|----------|------|------|------|
| `views/ai/chat.vue` | 知识问答 | adapt | 降级为辅助入口，不是核心 |
| `views/ai/analyze.vue` | AI 分析 | adapt | 纳入故障处置台 |
| `views/ai/copilot.vue` | AI Copilot | adapt | 改为故障分析助手 |
| `views/knowledge/list.vue` | 知识列表 | keep | |
| `views/knowledge/cases.vue` | 故障案例 | keep | |
| `views/knowledge/category.vue` | 知识分类 | keep | |

---

## 7. 平台管理台 (Platform Admin)

| 页面路径 | 功能 | 状态 | 说明 |
|----------|------|------|------|
| `views/system/user.vue` | 用户管理 | keep | |
| `views/system/role.vue` | 角色管理 | keep | |
| `views/system/menu.vue` | 菜单管理 | keep | |
| `views/system/config.vue` | 系统配置 | adapt | 拆分为平台配置和配置中心 |
| `views/system/dict.vue` | 字典管理 | keep | |
| `views/system/adapters.vue` | 适配器管理 | adapt | 协议适配器管理 |
| `views/system/logs.vue` | 系统日志 | keep | |
| `views/api-keys/index.vue` | API Key | keep | |
| `views/backup/list.vue` | 备份列表 | keep | |
| `views/backup/restore.vue` | 恢复备份 | keep | |
| `views/sharding/index.vue` | 分片管理 | keep | |
| `views/watermark/index.vue` | 水印管理 | keep | |
| `views/tenants/index.vue` | 租户管理 | adapt | 多租户管理 |

---

## 8. 工单 (Ticket)

| 页面路径 | 功能 | 状态 | 说明 |
|----------|------|------|------|
| `views/workorder/list.vue` | 工单列表 | keep | |
| `views/workorder/create.vue` | 创建工单 | keep | |
| `views/workorder/detail.vue` | 工单详情 | keep | 需增加关联日志/执行/AI分析 |
| `views/workorder/my.vue` | 我的工单 | keep | |

---

## 9. 巡检与报表 (Inspection & Report)

| 页面路径 | 功能 | 状态 | 说明 |
|----------|------|------|------|
| `views/inspection/tasks.vue` | 巡检任务 | keep | |
| `views/inspection/report.vue` | 巡检报告 | keep | |
| `views/report/list.vue` | 报表列表 | keep | |
| `views/report/create.vue` | 创建报表 | keep | |
| `views/report/template.vue` | 报表模板 | keep | |

---

## 10. 部署管理 (Deploy)

| 页面路径 | 功能 | 状态 | 说明 |
|----------|------|------|------|
| `views/deploy/health.vue` | 部署健康 | keep | |
| `views/deploy/versions.vue` | 版本管理 | keep | |
| `views/deploy/canary.vue` | 金丝雀部署 | keep | |

---

## 11. 已归档页面 (archive)

| 页面路径 | 状态 | 说明 |
|----------|------|------|
| `src/_archive_20250516/*` | archive | 旧版组件，已不再使用 |

---

## 前端目录重构目标

按目标架构，前端应重组为：

```
frontend/src/
  app/
    router/
    store/
    permission/
    layout/

  features/
    command-center/        # 运维指挥台
    asset-config/         # 资产与配置台
    monitoring-event/      # 监控与事件台
    incident-response/    # 故障处置台
    automation-orchestration/  # 自动化编排台
    aiops/                # AI 分析
    ticket/               # 工单
    knowledge/            # 知识
    platform-admin/        # 平台管理

  shared/
    api/
    components/
    hooks/
    utils/
    types/
    constants/
```

---

## 页面统计

| 状态 | 数量 | 说明 |
|------|------|------|
| keep | ~25 | 保留，直接使用 |
| adapt | ~20 | 需适配 |
| refactor | ~5 | 需重构 |
| archive | ~10 | 已归档 |

---

## 后续工作

1. 确定每个页面的路由路径和菜单归属
2. 设计故障处置台的页面布局
3. 设计自动化执行控制台的实时日志组件
4. 设计运维指挥台的卡片组件
5. 制定页面迁移计划
