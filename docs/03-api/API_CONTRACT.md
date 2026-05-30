# ITOps Platform API 契约文档

> 文档状态：current
> 版本：v1.0
> 基于：实际代码扫描生成（`api/routes/` + `app/domains/*/router.py`）
> 最后更新：2026-05-30

---

## 1. 统一响应格式

所有 API 必须返回以下统一格式（由 `app/common/response.py` 定义）：

```json
{
  "success": true,
  "code": "OK",
  "message": "success",
  "data": { ... },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 错误响应

```json
{
  "success": false,
  "code": "ASSET_NOT_FOUND",
  "message": "资产不存在",
  "data": null,
  "trace_id": "..."
}
```

### 分页响应

```json
{
  "success": true,
  "code": "OK",
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5
  },
  "trace_id": "..."
}
```

---

## 2. 统一错误码

由 `app/common/error_codes.py` 定义：

| 前缀 | 含义 |
|---|---|
| `ASSET_*` | 资产相关错误 |
| `CONFIG_*` | 配置相关错误 |
| `COLLECTOR_*` | 采集器相关错误 |
| `STATE_*` | 状态相关错误 |
| `EVENT_*` | 事件相关错误 |
| `ALERT_*` | 告警相关错误 |
| `LOG_*` | 日志相关错误 |
| `POLICY_*` | 策略相关错误 |
| `AUTOMATION_*` | 自动化相关错误 |
| `AIOPS_*` | AI 分析相关错误 |
| `TICKET_*` | 工单相关错误 |
| `KNOWLEDGE_*` | 知识库相关错误 |
| `AUTH_*` | 认证授权错误 |
| `SYSTEM_*` | 系统级错误 |

---

## 3. 认证

所有 API（除 `/auth/login`、`/health` 外）需要 JWT Bearer Token：

```
Authorization: Bearer <token>
```

登录接口：`POST /api/v1/auth/login`
```json
// Request
{ "username": "admin", "password": "Admin@123456" }
// Response
{ "success": true, "data": { "access_token": "...", "expires_in": 1800, "user": {...} } }
```

---

## 4. API 路由总览

### 4.1 旧路由（`api/routes/`）

| 模块 | 路径前缀 | 端点数 | 备注 |
|---|---|---|---|
| auth | `/api/v1/auth` | 15 | 认证 |
| user | `/api/v1/users` | ~30 | 用户管理 |
| system | `/api/v1/system` | ~20 | 系统配置 |
| asset | `/api/v1/assets` | ~25 | 资产管理（旧） |
| device_api | `/api/v1/devices` | ~20 | 设备管理（旧，与 asset 重复） |
| monitoring | `/api/v1/monitoring` | ~40 | 监控告警（旧） |
| notification | `/api/v1/notifications` | ~15 | 通知管理 |
| workorder | `/api/v1/workorders` | ~30 | 工单管理 |
| ai | `/api/v1/ai` | ~15 | AI 分析 |
| automation | `/api/v1/automation` | ~30 | 自动化执行 |
| knowledge | `/api/v1/knowledge` | ~20 | 知识库 |
| report | `/api/v1/reports` | ~15 | 报表 |
| discovery | `/api/v1/discovery` | ~10 | 设备发现 |
| device_import | `/api/v1/devices/import` | ~5 | 批量导入 |
| device_metrics | `/api/v1/device-metrics` | ~10 | 设备指标 |

### 4.2 新路由（`app/domains/*/router.py`）

| 领域 | 路径前缀 | 端点数 | 备注 |
|---|---|---|---|
| alert | `/api/v1/alerts` | ~25 | 告警管理（新） |
| asset_domain | `/api/v1/assets` | ~15 | 资产中心（新） |
| automation_domain | `/api/v1/automation` | ~20 | 自动化执行（新） |
| collector | `/api/v1/collectors` | ~15 | 采集器注册 |
| config | `/api/v1/configs` | ~20 | 配置管理 |
| event | `/api/v1/events` | ~15 | 事件管理 |
| log | `/api/v1/logs` | ~15 | 日志管理 |
| policy | `/api/v1/policies` | ~20 | 策略管理 |
| state | `/api/v1/state` | ~10 | 状态中心 |
| strategy | `/api/v1/strategies` | ~15 | 策略规则 |
| ticket | `/api/v1/tickets` | ~15 | 工单（新） |
| aiops | `/api/v1/aiops` | ~10 | AIops |
| governance | `/api/v1/governance` | ~10 | 治理 |
| knowledge_domain | `/api/v1/knowledge` | ~15 | 知识库（新） |

---

## 5. 核心 API 契约

### 5.1 资产

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/assets` | 资产列表（分页） |
| POST | `/api/v1/assets` | 创建资产 |
| GET | `/api/v1/assets/{id}` | 资产详情 |
| PUT | `/api/v1/assets/{id}` | 更新资产 |
| DELETE | `/api/v1/assets/{id}` | 删除资产 |
| POST | `/api/v1/assets/{id}/bind-credential` | 绑定凭证 |
| POST | `/api/v1/assets/{id}/bind-policy` | 绑定策略 |
| GET | `/api/v1/assets/{id}/relations` | 资产关系 |
| GET | `/api/v1/assets/{id}/state` | 资产状态 |

### 5.2 告警

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/alerts/` | 告警列表 |
| POST | `/api/v1/alerts/` | 创建告警 |
| GET | `/api/v1/alerts/{id}` | 告警详情（含证据链） |
| PUT | `/api/v1/alerts/{id}/acknowledge` | 确认告警 |
| PUT | `/api/v1/alerts/{id}/resolve` | 解决告警 |
| PUT | `/api/v1/alerts/{id}/close` | 关闭告警 |
| PUT | `/api/v1/alerts/{id}/transfer` | 转派告警 |
| GET | `/api/v1/alerts/{id}/evidence` | 告警证据（事件/日志/资产/AI分析） |
| GET | `/api/v1/alerts/stats` | 告警统计 |

### 5.3 事件

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/events` | 事件列表 |
| POST | `/api/v1/events` | 创建事件 |
| GET | `/api/v1/events/{id}` | 事件详情 |

### 5.4 自动化

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/automation/scripts` | 剧本列表 |
| POST | `/api/v1/automation/scripts/{id}/execute` | 执行剧本 |
| GET | `/api/v1/automation/executions` | 执行列表 |
| GET | `/api/v1/automation/executions/{id}` | 执行详情 |
| GET | `/api/v1/automation/executions/{id}/stream` | SSE 实时日志 |
| POST | `/api/v1/automation/executions/{id}/verify` | 验证执行结果 |
| POST | `/api/v1/automation/executions/{id}/rollback` | 回滚执行 |
| GET | `/api/v1/automation/approvals` | 审批列表 |
| POST | `/api/v1/automation/approvals/{id}/approve` | 审批通过 |
| POST | `/api/v1/automation/approvals/{id}/reject` | 审批拒绝 |
| POST | `/api/v1/automation/risk-assessment` | 风险评估 |
| POST | `/api/v1/automation/trigger-rules/{rule_id}` | 触发规则 |

### 5.5 策略

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/policies` | 策略列表 |
| POST | `/api/v1/policies` | 创建策略 |
| GET | `/api/v1/policies/{id}` | 策略详情 |
| PUT | `/api/v1/policies/{id}` | 更新策略 |
| POST | `/api/v1/policies/{id}/versions` | 创建版本 |
| POST | `/api/v1/policies/{id}/rollback` | 回滚策略 |
| POST | `/api/v1/policies/simulate` | 模拟策略命中 |
| POST | `/api/v1/policies/check-conflicts` | 检测冲突 |
| POST | `/api/v1/policies/match/{trigger_type}/explain` | 解释命中 |

### 5.6 AI 分析

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/ai/analyze` | 统一分析入口 |
| GET | `/api/v1/ai/analyze/history` | 分析历史 |
| POST | `/api/v1/ai/analyze/{alert_id}/root-cause` | 根因分析 |
| POST | `/api/v1/ai/analyze/{alert_id}/remediation` | 修复建议 |
| POST | `/api/v1/ai/interpret-log` | 日志解释（规则引擎，支持 12 种错误模式） |
| POST | `/api/v1/ai/feedback/score` | 反馈打分 |
| POST | `/api/v1/ai/feedback/acknowledge` | 反馈确认 |

### 5.7 知识库

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/knowledge/articles` | 知识列表 |
| POST | `/api/v1/knowledge/articles` | 创建知识 |
| GET | `/api/v1/knowledge/articles/{id}` | 知识详情 |
| GET | `/api/v1/knowledge/search` | 知识搜索 |

### 5.8 工单

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/workorders` | 工单列表 |
| POST | `/api/v1/workorders` | 创建工单 |
| GET | `/api/v1/workorders/{id}` | 工单详情 |
| PUT | `/api/v1/workorders/{id}` | 更新工单 |
| POST | `/api/v1/workorders/{id}/assign` | 分配工单 |
| POST | `/api/v1/workorders/{id}/close` | 关闭工单 |
| POST | `/api/v1/workorders/{id}/transfer` | 转化工单 |
| GET | `/api/v1/workorders/{id}/evidence` | 工单证据 |

### 5.9 日志与审计

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/logs/executions/{name}/{id}/logs` | 执行日志 |
| GET | `/api/v1/logs/audit` | 审计日志 |

### 5.10 采集器

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/collectors/register` | 注册采集器 |
| POST | `/api/v1/collectors/heartbeat` | 采集器心跳 |
| GET | `/api/v1/collectors/list` | 采集器列表 |
| GET | `/api/v1/collectors/stats` | 采集器统计 |
| GET | `/api/v1/collectors/state/{id}` | 采集器状态 |

---

## 6. WebSocket / SSE

| 路径 | 类型 | 说明 |
|---|---|---|
| `/api/v1/automation/executions/{id}/stream` | SSE | 自动化执行实时日志 |
| `/api/v1/events/stream` | SSE | 事件流（待实现） |

---

## 7. 认证与权限

- 所有接口需要登录（`/auth/login` 除外）
- 用户角色：admin / operator / viewer
- 权限通过 `@require_permission` 装饰器控制

---

## 8. API 版本

当前版本：`v1`
Base Path：`/api/v1`

---

## 9. 待完善接口（按 DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md）

以下接口在文档中有规划但尚未实现或验证：

| 接口 | 状态 | 说明 |
|---|---|---|
| `GET /api/v1/assets/{id}/timeline` | 待验证 | 资产生命周期时间线 |
| `POST /api/v1/config/diff` | 待验证 | 配置差异比对 |
| `POST /api/v1/config/releases/{id}/rollback` | 待验证 | 配置回滚 |
| `GET /api/v1/state/assets/{id}/state` | 待验证 | 资产当前状态 |
| WebSocket 状态推送 | 待实现 | 前端订阅资产状态变化 |
