# 前端页面API调用审查报告

**审查时间**: 2026-05-28 01:21
**审查范围**: `/home/zcxx/.hermes/projects/itops_platform/frontend/src/views/**/*.vue`
**后端服务**: http://localhost:8000/api/v1

---

## 一、API文件清单

### 1.1 前端API模块 (frontend/src/api/)
| 文件 | 描述 |
|------|------|
| `request.js` | Axios请求封装，baseURL: `/api/v1` |
| `index.js` | API统一导出 |
| `monitoring.js` | 监控相关API (devices, alerts, performance, dashboards, maintenanceWindows, triggerRules, metricConfigs) |
| `system.js` | 系统API (auth, user, role, menu, dict, config, system) |
| `workorder.js` | 工单API |
| `assets.js` | 资产API |
| `discovery.js` | 发现API |
| `automation.js` | 自动化API |
| `inspection.js` | 巡检API |
| `deploy.js` | 部署API |
| `knowledge.js` | 知识库API |
| `notification.js` | 通知API |
| `tenants.js` | 租户API |
| `apiKeys.js` | API Key管理API |
| `sharding.js` | 分片API |
| `watermark.js` | 水印API |
| `scheduler.js` | 调度API |

### 1.2 Vue页面文件 (50个)
覆盖: dashboard, monitoring, workorder, automation, discovery, knowledge, inspection, deploy, notification, system, tenants, api-keys, watermark, backup, login等模块

---

## 二、API验证结果汇总

### 2.1 ✅ 验证通过 (API存在且正常)

| API端点 | 方法 | 验证结果 |
|---------|------|----------|
| `/auth/login` | POST | ✅ 正常 |
| `/auth/userinfo` | GET | ✅ 正常 |
| `/assets/device` | GET/POST | ✅ 正常 |
| `/assets/device/{id}` | GET/PUT/DELETE | ✅ 正常 |
| `/assets/stats` | GET | ✅ 正常 |
| `/monitoring/alerts` | GET | ✅ 正常 |
| `/monitoring/alerts/statistics` | GET | ✅ 正常 |
| `/monitoring/dashboards` | GET | ✅ 正常 |
| `/monitoring/dashboard/layout` | GET/PUT | ✅ 正常 |
| `/monitoring/dashboard/stats` | GET | ✅ 正常 |
| `/monitoring/maintenance-windows` | GET/POST | ✅ 正常 |
| `/monitoring/metrics` | GET | ✅ 正常 |
| `/monitoring/metrics/hosts` | GET | ✅ 正常 |
| `/monitoring/metrics/available` | GET | ✅ 正常 |
| `/monitoring/metrics/query` | POST | ✅ 正常 |
| `/monitoring/metrics/history` | GET | ✅ 正常 |
| `/monitoring/metrics/top/{type}` | GET | ✅ 正常 |
| `/monitoring/rules` | GET | ✅ 正常 (返回空列表) |
| `/monitoring/trigger-rules` | GET | ✅ 正常 (返回空列表) |
| `/monitoring/metric-configs` | GET | ✅ 正常 (返回空列表) |
| `/workorders/` | GET/POST | ✅ 正常 |
| `/workorders/{id}` | GET/PUT/DELETE | ✅ 正常 |
| `/workorders/categories` | GET | ✅ 正常 |
| `/workorders/priorities` | GET | ✅ 正常 |
| `/workorders/stats/summary` | GET | ✅ 正常 |
| `/workorders/stats/trend` | GET | ✅ 正常 |
| `/workorders/{id}/flows` | GET | ✅ 正常 |
| `/workorders/{id}/sla` | GET | ✅ 正常 |
| `/workorders/{id}/approval-flow` | GET | ✅ 正常 |
| `/workorders/draft/list` | GET | ✅ 正常 |
| `/workorders/draft/save` | POST | ✅ 正常 |
| `/admin/users` | GET | ✅ 正常 |
| `/admin/roles` | GET | ✅ 正常 |
| `/admin/menu` | GET | ✅ 正常 |
| `/admin/dict` | GET | ✅ 正常 |
| `/admin/config` | GET | ✅ 正常 |
| `/admin/info` | GET | ✅ 正常 |
| `/admin/health` | GET | ✅ 正常 |
| `/admin/metrics` | GET | ✅ 正常 |
| `/admin/logs` | GET | ✅ 正常 |
| `/admin/permissions` | GET | ✅ 正常 |
| `/discovery/networks` | GET | ✅ 正常 |
| `/discovery/scan-history` | GET | ✅ 正常 |
| `/automation/scripts` | GET | ✅ 正常 |
| `/automation/tasks` | GET | ✅ 正常 |
| `/automation/executions` | GET | ✅ 正常 |
| `/automation/trigger-rules` | GET | ✅ 正常 |
| `/automation/rollback-history` | GET | ✅ 正常 |
| `/inspection/tasks` | GET | ✅ 正常 |
| `/inspection/reports/{taskId}` | GET | ✅ 正常 |
| `/inspection/reports/template` | GET | ✅ 正常 |
| `/inspection/statistics/summary` | GET | ✅ 正常 |
| `/knowledge/sop` | GET | ✅ 正常 |
| `/knowledge/search` | GET | ✅ 正常 |
| `/knowledge/fault-case` | GET | ✅ 正常 |
| `/knowledge/category` | GET | ✅ 正常 |
| `/knowledge/reviews` | GET | ✅ 正常 |
| `/tenants` | GET | ✅ 正常 |
| `/api-keys` | GET | ✅ 正常 |
| `/sharding/stats` | GET | ✅ 正常 |
| `/watermark/list` | GET | ✅ 正常 |
| `/notifications/channels` | GET | ✅ 正常 |
| `/notifications/messages` | GET | ✅ 正常 |
| `/notifications/target-rules` | GET | ✅ 正常 |
| `/notifications/targets` | GET | ✅ 正常 |
| `/notifications/types` | GET | ✅ 正常 |
| `/deploy/health` | GET | ✅ 正常 |
| `/deploy/versions` | GET | ✅ 正常 (返回空) |
| `/deploy/canary` | GET | ✅ 正常 (返回空) |
| `/deploy/history` | GET | ✅ 正常 (返回空) |
| `/ai/stats` | GET | ✅ 正常 |
| `/devices/{name}/metrics` | GET | ✅ 正常 (返回离线状态) |
| `/devices/{name}/status` | GET | ✅ 正常 |
| `/devices/stats` | GET | ✅ 正常 |

### 2.2 ⚠️ 存在问题

| API端点 | 问题 | 严重程度 |
|---------|------|----------|
| `/workorders/convert-to-workorder` | POST返回500内部错误 | 🔴 高 |
| `/devices/collect` | 需要`device_name`字段而非`device_id` | 🟡 中 |
| `/ai/chat` | 需要`sessions`或`conversation_id`字段 | 🟡 中 |
| `/ai/troubleshoot` | 需要`symptom`等必填字段 | 🟡 中 |
| `/ai/analyze` | 需要`target_type`, `target_id`字段 | 🟡 中 |
| `/ai/qa` | 需要`query.question`格式 | 🟡 中 |
| `/watermark/generate` | 需要`action`, `resource`, `resource_id`字段 | 🟡 中 |
| `/notifications/send` | 需要`type`, `title`, `webhook_url`字段 | 🟡 中 |
| `/discovery/scan` | 需要`cidr`而非`ip_range`字段 | 🟡 中 |
| `/discovery/devices/import` | 需要`ips`数组字段 | 🟡 中 |
| `/devices/{name}/metrics/history` | 离线设备无数据返回404 | 🟢 低 |

---

## 三、字段名匹配问题

### 3.1 🔴 工单优先级字段不匹配

**前端 (workorder.js)**:
```javascript
// 调用 getStats()
statCardValues.value = [
  data.total,
  data.online || 0,
  statCardValues.value[2],
  data.pending_orders || 0
]
```

**后端返回** (`/workorders/stats/summary`):
```json
{
  "total": 16,
  "pending": 15,
  "by_priority": {"P1": 3, "P2": 7, "P3": 6, "P4": 0}
}
```

**问题**: 后端返回 `by_priority` 使用 `P1/P2/P3/P4`，但前端可能期望 `urgent/high/medium/low`

### 3.2 🔴 告警级别字段不匹配

**前端期望** (alerts.vue):
```javascript
const severityTypeMap = { critical: 'danger', high: 'danger', medium: 'warning', low: 'info', info: 'info' }
```

**后端返回** (`/monitoring/alerts`):
```json
{
  "level": "critical",
  "status": "resolved"
}
```

**状态**: ✅ 基本匹配，但需要确认 `warning` 级别是否映射正确

### 3.3 🟡 设备状态字段

**后端返回** (`/devices/{name}/status`):
```json
{
  "device_name": "zcxxclow",
  "status": "DeviceStatus.OFFLINE",
  "last_update": "2026-05-28T01:21:11.705159"
}
```

**问题**: 状态值包含 `DeviceStatus.` 前缀，前端可能需要处理

### 3.4 🟡 仪表盘布局API响应格式

**前端期望**:
```javascript
const layout = layoutRes?.data || layoutRes
if (layout && layout.items) {
  allItems.value = layout.items.map(...)
}
```

**后端返回** (`/monitoring/dashboard/layout`):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "layout_id": "default_xxx",
    "items": [...]
  }
}
```

**状态**: ✅ 前端已有 `layoutRes?.data` 解包处理，兼容

---

## 四、API路径问题

### 4.1 导入设备API路径重复定义

**assets.js**:
```javascript
getImportTemplate: (format = 'xlsx') => request.get('/template', ...),
validateImport: (rows) => request.post('/validate', rows),
importDevices: (file) => request.post('/', formData, ...),
importDevicesSimple: (rows) => request.post('/simple', rows)
```

**问题**: 这些API路径没有前缀，可能与设备导入路由冲突

### 4.2 设备指标采集API

**前端调用** (`/devices/collect`):
```javascript
collect: (data) => request.post('/devices/collect', data),
```

**实际需要** (后端验证):
```json
{
  "detail": [
    {"type": "missing", "loc": ["body", "device_name"], "msg": "Field required"}
  ]
}
```

---

## 五、建议修复项

### 5.1 高优先级 🔴

1. **工单转告警接口** `/workorders/convert-to-workorder` 返回500错误，需检查后端实现

2. **工单优先级枚举统一**:
   - 建议后端增加 `by_type` 映射，将 `P1/P2/P3/P4` 映射为 `urgent/high/medium/low`
   - 或前端适配 `P1-P4` 格式

### 5.2 中优先级 🟡

3. **设备采集接口参数**: 前端发送 `device_id`，后端需要 `device_name`

4. **AI接口字段规范**: 统一 `ai/chat`, `ai/troubleshoot`, `ai/analyze` 的请求格式

5. **发现扫描接口**: `ip_range` 应改为 `cidr`

### 5.3 低优先级 🟢

6. **设备状态值前缀**: `DeviceStatus.OFFLINE` 应处理为 `offline`

7. **离线设备指标历史**: 返回 `设备无指标数据` 而非404

---

## 六、测试账号

- 用户名: `admin`
- 密码: `Admin@123456`
- Token有效期: 30分钟

---

*报告生成时间: 2026-05-28 01:21*
