# P0-2 前后端接口契约自动化比对报告

- 前端 API 调用：333 条，去重后 331 条
- 后端 OpenAPI 路由：343 条，规范化后 343 条
- 候选差异：14 条

## 候选差异与 HTTP 验证

| 文件 | 前端方法 | 规范化路径 | 后端同路径方法 | 类型 | 实测状态 | 原始路径 |
|---|---|---|---|---|---:|---|
| `frontend/src/api/workorder.js` | PUT | `/api/v1/workorders/{id}/resolve` | POST | METHOD_MISMATCH | 405 | `/workorders/${id}/resolve` |
| `frontend/src/api/system.js` | PUT | `/api/v1/admin/users/{id}/status` | - | MISSING_PATH | 405 | `/admin/users/${id}/status` |
| `frontend/src/api/system.js` | GET | `/api/v1/admin/roles/{id}` | DELETE,PUT | METHOD_MISMATCH | 404 | `/admin/roles/${id}` |
| `frontend/src/api/system.js` | GET | `/api/v1/admin/config/{id}` | PUT | METHOD_MISMATCH | 404 | `/admin/config/${key}` |
| `frontend/src/api/monitoring.js` | GET | `/api/v1/devices-import/template` | - | MISSING_PATH | 404 | `/devices-import/template` |
| `frontend/src/api/monitoring.js` | POST | `/api/v1/devices-import/validate` | - | MISSING_PATH | 405 | `/devices-import/validate` |
| `frontend/src/api/monitoring.js` | POST | `/api/v1/devices-import` | - | MISSING_PATH | 405 | `/devices-import` |
| `frontend/src/api/monitoring.js` | POST | `/api/v1/devices-import/simple` | - | MISSING_PATH | 405 | `/devices-import/simple` |
| `frontend/src/api/monitoring.js` | PUT | `/api/v1/monitoring/alerts/{id}` | DELETE,GET | METHOD_MISMATCH | 405 | `/monitoring/alerts/${id}` |
| `frontend/src/api/monitoring.js` | PUT | `/api/v1/monitoring/metric-configs/{id}/toggle` | PATCH | METHOD_MISMATCH | 405 | `/monitoring/metric-configs/${id}/toggle` |
| `frontend/src/api/discovery.js` | GET | `/api/v1/discovery/networks/{id}` | DELETE,PUT | METHOD_MISMATCH | 404 | `/discovery/networks/${id}` |
| `frontend/src/api/knowledge.js` | DELETE | `/api/v1/knowledge/fault-case/{id}` | GET,PUT | METHOD_MISMATCH | 405 | `/knowledge/fault-case/${id}` |
| `frontend/src/api/knowledge.js` | PUT | `/api/v1/knowledge/category/{id}` | - | MISSING_PATH | 405 | `/knowledge/category/${id}` |
| `frontend/src/api/knowledge.js` | DELETE | `/api/v1/knowledge/category/{id}` | - | MISSING_PATH | 405 | `/knowledge/category/${id}` |

## 初步判定

- `405`：真实方法不匹配，优先改前端调用方法。
- `404`：真实路径缺失，需判断是前端旧路径还是后端缺接口。
- `401/403/422/200`：说明路由层存在，需结合认证/参数继续业务验证。
