# ITOps Platform 错误码体系

> 文档状态：current
> 版本：v1.0
> 事实源：`app/common/error_codes.py`（代码即文档）
> 最后更新：2026-05-30

---

## 1. 错误码分类

| 前缀 | 含义 | HTTP 4xx | HTTP 5xx |
|---|---|---|---|
| `ASSET_*` | 资产相关 | 404, 409, 422 | 500 |
| `CONFIG_*` | 配置相关 | 404, 409 | 500 |
| `COLLECTOR_*` | 采集器相关 | 404, 422 | 500, 504 |
| `STATE_*` | 状态相关 | 404 | 500 |
| `EVENT_*` | 事件相关 | 404 | 500 |
| `ALERT_*` | 告警相关 | 404, 400 | 500 |
| `LOG_*` | 日志相关 | 404 | 500 |
| `POLICY_*` | 策略相关 | 404, 409 | 500 |
| `AUTOMATION_*` | 自动化相关 | 403, 404 | 500 |
| `AIOPS_*` | AI 分析相关 | 403 | 500, 503 |
| `TICKET_*` | 工单相关 | 404 | 500 |
| `KNOWLEDGE_*` | 知识库相关 | 404 | 500 |
| `AUTH_*` | 认证授权 | 401, 403 | — |
| `SYSTEM_*` | 系统级 | 400, 404, 409, 422, 429 | 500, 503 |

---

## 2. 错误码详细列表

### ASSET_* — 资产

| 错误码 | HTTP | 说明 |
|---|---|---|
| `ASSET_NOT_FOUND` | 404 | 资产不存在 |
| `ASSET_ALREADY_EXISTS` | 409 | 资产已存在 |
| `ASSET_CREATE_FAILED` | 500 | 创建资产失败 |
| `ASSET_UPDATE_FAILED` | 500 | 更新资产失败 |
| `ASSET_DELETE_FAILED` | 500 | 删除资产失败 |
| `ASSET_VALIDATION_FAILED` | 422 | 资产数据校验失败 |
| `ASSET_BINDING_FAILED` | 500 | 资产绑定失败 |

### CONFIG_* — 配置

| 错误码 | HTTP | 说明 |
|---|---|---|
| `CONFIG_NOT_FOUND` | 404 | 配置不存在 |
| `CONFIG_ALREADY_EXISTS` | 409 | 配置已存在 |
| `CONFIG_CREATE_FAILED` | 500 | 创建配置失败 |
| `CONFIG_UPDATE_FAILED` | 500 | 更新配置失败 |
| `CONFIG_DELETE_FAILED` | 500 | 删除配置失败 |
| `CONFIG_VERSION_CONFLICT` | 409 | 配置版本冲突 |
| `CONFIG_RELEASE_FAILED` | 500 | 配置发布失败 |
| `CONFIG_ROLLBACK_FAILED` | 500 | 配置回滚失败 |

### COLLECTOR_* — 采集器

| 错误码 | HTTP | 说明 |
|---|---|---|
| `COLLECTOR_NOT_FOUND` | 404 | 采集器不存在 |
| `COLLECTOR_CONNECTION_FAILED` | 500 | 采集器连接失败 |
| `COLLECTOR_COLLECT_FAILED` | 500 | 采集失败 |
| `COLLECTOR_TIMEOUT` | 504 | 采集器超时 |
| `COLLECTOR_UNSUPPORTED_PROTOCOL` | 422 | 不支持的协议 |

### STATE_* — 状态

| 错误码 | HTTP | 说明 |
|---|---|---|
| `STATE_NOT_FOUND` | 404 | 状态不存在 |
| `STATE_UPDATE_FAILED` | 500 | 状态更新失败 |
| `STATE_HISTORY_NOT_FOUND` | 404 | 状态历史不存在 |

### EVENT_* — 事件

| 错误码 | HTTP | 说明 |
|---|---|---|
| `EVENT_NOT_FOUND` | 404 | 事件不存在 |
| `EVENT_CREATE_FAILED` | 500 | 事件创建失败 |
| `EVENT_CORRELATION_FAILED` | 500 | 事件关联失败 |

### ALERT_* — 告警

| 错误码 | HTTP | 说明 |
|---|---|---|
| `ALERT_NOT_FOUND` | 404 | 告警不存在 |
| `ALERT_CREATE_FAILED` | 500 | 告警创建失败 |
| `ALERT_UPDATE_FAILED` | 500 | 告警更新失败 |
| `ALERT_RESOLVE_FAILED` | 500 | 告警解决失败 |
| `ALERT_TRANSFER_FAILED` | 500 | 告警转派失败 |
| `ALERT_SUPPRESS_FAILED` | 500 | 告警抑制失败 |
| `ALERT_SUPPRESSED` | 400 | 告警被抑制 |
| `ALERT_ESCALATE_FAILED` | 500 | 告警升级失败 |
| `ALERT_CONSOLIDATION_FAILED` | 500 | 告警合并失败 |
| `ALERT_RULE_NOT_FOUND` | 404 | 告警规则不存在 |
| `ALERT_RULE_CREATE_FAILED` | 500 | 告警规则创建失败 |
| `ALERT_RULE_UPDATE_FAILED` | 500 | 告警规则更新失败 |
| `ALERT_RULE_DELETE_FAILED` | 500 | 告警规则删除失败 |
| `ALERT_TRIGGER_FAILED` | 500 | 告警触发失败 |
| `ALERT_EVALUATION_FAILED` | 500 | 告警评估失败 |

### LOG_* — 日志

| 错误码 | HTTP | 说明 |
|---|---|---|
| `LOG_NOT_FOUND` | 404 | 日志不存在 |
| `LOG_CREATE_FAILED` | 500 | 日志创建失败 |
| `LOG_QUERY_FAILED` | 500 | 日志查询失败 |
| `LOG_CONFIG_NOT_FOUND` | 404 | 日志配置不存在 |
| `LOG_CONFIG_UPDATE_FAILED` | 500 | 日志配置更新失败 |
| `LOG_INDEX_NOT_FOUND` | 404 | 日志索引不存在 |
| `LOG_INDEX_CREATE_FAILED` | 500 | 日志索引创建失败 |
| `LOG_INDEX_DELETE_FAILED` | 500 | 日志索引删除失败 |
| `LOG_ACCESS_CONFIG_NOT_FOUND` | 404 | 日志访问配置不存在 |
| `LOG_ACCESS_CONFIG_UPDATE_FAILED` | 500 | 日志访问配置更新失败 |
| `LOG_GROUP_NOT_FOUND` | 404 | 日志组不存在 |
| `LOG_ITEM_NOT_FOUND` | 404 | 日志项不存在 |

### POLICY_* — 策略

| 错误码 | HTTP | 说明 |
|---|---|---|
| `POLICY_NOT_FOUND` | 404 | 策略不存在 |
| `POLICY_ALREADY_EXISTS` | 409 | 策略已存在 |
| `POLICY_CREATE_FAILED` | 500 | 策略创建失败 |
| `POLICY_UPDATE_FAILED` | 500 | 策略更新失败 |
| `POLICY_DELETE_FAILED` | 500 | 策略删除失败 |
| `POLICY_SIMULATE_FAILED` | 500 | 策略模拟失败 |
| `POLICY_CONFLICT` | 409 | 策略冲突 |
| `POLICY_HIT_FAILED` | 500 | 策略命中失败 |

### AUTOMATION_* — 自动化

| 错误码 | HTTP | 说明 |
|---|---|---|
| `AUTOMATION_NOT_FOUND` | 404 | 自动化不存在 |
| `AUTOMATION_CREATE_FAILED` | 500 | 自动化创建失败 |
| `AUTOMATION_UPDATE_FAILED` | 500 | 自动化更新失败 |
| `AUTOMATION_DELETE_FAILED` | 500 | 自动化删除失败 |
| `AUTOMATION_EXECUTE_FAILED` | 500 | 自动化执行失败 |
| `AUTOMATION_ROLLBACK_FAILED` | 500 | 自动化回滚失败 |
| `AUTOMATION_DRYRUN_FAILED` | 500 | 自动化试运行失败 |
| `AUTOMATION_APPROVAL_REQUIRED` | 403 | 需要审批 |
| `AUTOMATION_RISK_TOO_HIGH` | 403 | 风险过高 |
| `AUTOMATION_LOCK_FAILED` | 500 | 自动化加锁失败 |
| `AUTOMATION_VERIFY_FAILED` | 500 | 自动化验证失败 |

### AIOPS_* — AI 分析

| 错误码 | HTTP | 说明 |
|---|---|---|
| `AIOPS_ANALYSIS_FAILED` | 500 | AI 分析失败 |
| `AIOPS_CONTEXT_BUILD_FAILED` | 500 | AI 上下文构建失败 |
| `AIOPS_LLM_UNAVAILABLE` | 503 | LLM 服务不可用 |
| `AIOPS_TOOL_FORBIDDEN` | 403 | AI 工具调用被禁止 |

### TICKET_* — 工单

| 错误码 | HTTP | 说明 |
|---|---|---|
| `TICKET_NOT_FOUND` | 404 | 工单不存在 |
| `TICKET_CREATE_FAILED` | 500 | 工单创建失败 |
| `TICKET_UPDATE_FAILED` | 500 | 工单更新失败 |
| `TICKET_ASSIGN_FAILED` | 500 | 工单分配失败 |
| `TICKET_APPROVE_FAILED` | 500 | 工单审批失败 |
| `TICKET_REJECT_FAILED` | 500 | 工单拒绝失败 |
| `TICKET_CLOSE_FAILED` | 500 | 工单关闭失败 |

### KNOWLEDGE_* — 知识库

| 错误码 | HTTP | 说明 |
|---|---|---|
| `KNOWLEDGE_NOT_FOUND` | 404 | 知识不存在 |
| `KNOWLEDGE_CREATE_FAILED` | 500 | 知识创建失败 |
| `KNOWLEDGE_UPDATE_FAILED` | 500 | 知识更新失败 |
| `KNOWLEDGE_DELETE_FAILED` | 500 | 知识删除失败 |
| `KNOWLEDGE_REVIEW_FAILED` | 500 | 知识审核失败 |
| `KNOWLEDGE_APPROVE_FAILED` | 500 | 知识批准失败 |
| `KNOWLEDGE_REJECT_FAILED` | 500 | 知识拒绝失败 |

### AUTH_* — 认证授权

| 错误码 | HTTP | 说明 |
|---|---|---|
| `AUTH_FAILED` | 401 | 认证失败 |
| `AUTH_TOKEN_EXPIRED` | 401 | Token 过期 |
| `AUTH_TOKEN_INVALID` | 401 | Token 无效 |
| `AUTH_PERMISSION_DENIED` | 403 | 权限不足 |
| `AUTH_CREDENTIAL_INVALID` | 401 | 凭证无效 |
| `AUTH_USER_NOT_FOUND` | 401 | 用户不存在 |
| `AUTH_LDAP_FAILED` | 401 | LDAP 认证失败 |

### SYSTEM_* — 系统级

| 错误码 | HTTP | 说明 |
|---|---|---|
| `SYSTEM_INTERNAL_ERROR` | 500 | 内部错误 |
| `SYSTEM_DATABASE_ERROR` | 500 | 数据库错误 |
| `SYSTEM_REDIS_ERROR` | 500 | Redis 错误 |
| `SYSTEM_QUEUE_ERROR` | 500 | 队列错误 |
| `SYSTEM_VALIDATION_ERROR` | 422 | 校验错误 |
| `SYSTEM_RESOURCE_NOT_FOUND` | 404 | 资源不存在 |
| `SYSTEM_RESOURCE_CONFLICT` | 409 | 资源冲突 |
| `SYSTEM_RATE_LIMITED` | 429 | 请求过于频繁 |
| `SYSTEM_UNAVAILABLE` | 503 | 服务不可用 |

---

## 3. HTTP 状态码速查

| HTTP 状态码 | 含义 | 常见错误码 |
|---|---|---|
| 200 | 成功 | `OK` |
| 400 | 客户端错误 | `ALERT_SUPPRESSED` |
| 401 | 未认证 | `AUTH_FAILED`, `AUTH_TOKEN_EXPIRED`, `AUTH_TOKEN_INVALID`, `AUTH_CREDENTIAL_INVALID`, `AUTH_USER_NOT_FOUND`, `AUTH_LDAP_FAILED` |
| 403 | 禁止 | `AUTH_PERMISSION_DENIED`, `AUTOMATION_APPROVAL_REQUIRED`, `AUTOMATION_RISK_TOO_HIGH`, `AIOPS_TOOL_FORBIDDEN` |
| 404 | 不存在 | `ASSET_NOT_FOUND`, `CONFIG_NOT_FOUND`, `COLLECTOR_NOT_FOUND`, `STATE_NOT_FOUND`, `EVENT_NOT_FOUND`, `ALERT_NOT_FOUND`, `LOG_NOT_FOUND`, `POLICY_NOT_FOUND`, `AUTOMATION_NOT_FOUND`, `TICKET_NOT_FOUND`, `KNOWLEDGE_NOT_FOUND` |
| 409 | 冲突 | `ASSET_ALREADY_EXISTS`, `CONFIG_ALREADY_EXISTS`, `CONFIG_VERSION_CONFLICT`, `POLICY_ALREADY_EXISTS`, `POLICY_CONFLICT`, `SYSTEM_RESOURCE_CONFLICT` |
| 422 | 校验失败 | `ASSET_VALIDATION_FAILED`, `COLLECTOR_UNSUPPORTED_PROTOCOL`, `SYSTEM_VALIDATION_ERROR` |
| 429 | 限流 | `SYSTEM_RATE_LIMITED` |
| 500 | 服务器错误 | 所有 `*_FAILED` 错误码 |
| 503 | 服务不可用 | `AIOPS_LLM_UNAVAILABLE`, `SYSTEM_UNAVAILABLE` |
| 504 | 超时 | `COLLECTOR_TIMEOUT` |

---

## 4. 响应示例

### 认证失败（401）
```json
{
  "success": false,
  "code": "AUTH_TOKEN_EXPIRED",
  "message": "Token 已过期，请重新登录",
  "data": null,
  "trace_id": "..."
}
```

### 资源不存在（404）
```json
{
  "success": false,
  "code": "ASSET_NOT_FOUND",
  "message": "资产不存在",
  "data": null,
  "trace_id": "..."
}
```

### 服务器内部错误（500）
```json
{
  "success": false,
  "code": "SYSTEM_INTERNAL_ERROR",
  "message": "Internal server error",
  "data": null,
  "trace_id": "..."
}
```
