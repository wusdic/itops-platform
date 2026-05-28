# ITOPS 平台文档总入口

> 文档状态：current
> 适用版本：v2.0+
> 最后更新：2026-05-28
> 维护人：ITOPS 开发团队

---

## 单一事实源

所有开发、架构、评审均以本文档目录下的文档为准。旧文档已归档至 `docs/99-archive/`，不再作为开发依据。

---

## 文档目录

### 00-overview/ （本文档）
- [PRODUCT_POSITIONING.md](./PRODUCT_POSITIONING.md) — 产品定位
- [ROADMAP.md](./ROADMAP.md) — 开发路线图

### 01-architecture/
- **[AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md](../01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md)** ⭐ 最高级别架构依据
- BACKEND_ARCHITECTURE.md — 后端架构（待编写）
- FRONTEND_ARCHITECTURE.md — 前端架构（待编写）
- DATA_ARCHITECTURE.md — 数据架构（待编写）
- EVENT_DRIVEN_ARCHITECTURE.md — 事件驱动架构（待编写）
- SECURITY_ARCHITECTURE.md — 安全架构（待编写）
- adr/ — 架构决策记录（ADR）

### 02-domains/
各领域详细设计文档（按阶段逐步编写）

### 03-api/
- API_CONTRACT.md — API 契约
- ERROR_CODES.md — 错误码定义
- AUTH_AND_PERMISSION.md — 认证与权限
- WEBSOCKET_EVENTS.md — WebSocket 事件

### 04-frontend/
- UX_WORKFLOWS.md — 用户体验工作流
- PAGE_STRUCTURE.md — 页面结构
- COMPONENT_GUIDE.md — 组件指南
- INCIDENT_RESPONSE_UI.md — 故障处置台 UI

### 05-implementation/
- **[DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md](../05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md)** ⭐ 开发计划与代码取舍
- CODE_INVENTORY.md — 代码清单（待生成）
- API_INVENTORY.md — API 路由清单（待生成）
- FRONTEND_PAGE_INVENTORY.md — 前端页面清单（待生成）
- TESTING_STRATEGY.md — 测试策略
- ACCEPTANCE_CRITERIA.md — 验收标准

### 06-operations/
- DEPLOYMENT.md — 部署文档
- BACKUP_RESTORE.md — 备份恢复
- OBSERVABILITY.md — 可观测性
- SECURITY.md — 安全运维
- PLATFORM_SELF_CHECK.md — 平台自检

### 99-archive/
已归档的旧文档，不再作为开发依据。

---

## 快速链接

- [架构总纲](../01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md)
- [详细开发计划](../05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md)

---

## 文档更新规则

任何 PR 涉及以下内容，必须同步更新对应文档：
- 新增或修改领域模型
- 新增或修改 API
- 新增或修改数据库表
- 新增或修改配置项
- 新增或修改采集器
- 新增或修改事件类型
- 新增或修改策略
- 新增或修改自动化动作
- 新增或修改前端页面
- 新增或修改权限
- 新增或修改部署方式

## PR 检查清单

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
