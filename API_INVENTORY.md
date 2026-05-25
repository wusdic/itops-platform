# ITOps Platform API 清单

> 生成时间: 2026-05-25  
> API Base: http://localhost:8000  
> OpenAPI: /openapi.json

---

## 一、API 汇总统计

| 模块 | API 数量 | 说明 |
|------|---------|------|
| 系统管理 (admin) | ~90 | 用户、角色、菜单、配置、备份、日志等 |
| 监控管理 (monitoring) | ~35 | 告警、指标、仪表盘、维护时段、触发规则 |
| 设备管理 (devices) | ~30 | 设备列表、采集、配置 |
| 资产管理 (assets) | ~25 | 设备、业务系统、配置项 |
| 工单管理 (workorders) | ~30 | 工单、流程、草稿、SLA |
| 知识库 (knowledge) | ~30 | SOP、故障案例、图谱、审核 |
| 自动化 (automation) | ~25 | 脚本、任务、触发规则、执行 |
| 报表 (reports) | ~20 | 模板、生成、调度 |
| 巡检 (inspection) | ~10 | 巡检任务、报告 |
| 通知 (notifications) | ~20 | 渠道、消息、目标规则 |
| 部署 (deploy) | ~15 | 金丝雀、版本、健康 |
| 设备发现 (discovery) | ~25 | 扫描、导入、网络 |
| AI 助手 (ai) | ~15 | 对话、分析、根因、故障排查 |
| 认证 (auth) | ~10 | 登录、登出、刷新、注册 |
| 厂商账密 (credentials) | ~15 | 厂商、版本、探测 |
| 系统适配 (system) | ~5 | 菜单 |
| 其他 | ~10 | 分片、水印、租户、报表别名 |
| **总计** | **~400** | |

---

## 二、API 详情（按模块分组）

### 2.1 系统管理 (admin) - 标注: ✅前端已对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/admin/info | 获取系统信息 | App.vue | ✅ |
| GET | /api/v1/admin/health | 系统健康检查 | - | ❌ |
| GET | /api/v1/admin/users | 获取用户列表 | system/user.vue | ✅ |
| POST | /api/v1/admin/users | 创建用户 | system/user.vue | ✅ |
| GET | /api/v1/admin/users/{user_id} | 获取用户详情 | system/user.vue | ✅ |
| PUT | /api/v1/admin/users/{user_id} | 更新用户 | system/user.vue | ✅ |
| DELETE | /api/v1/admin/users/{user_id} | 删除用户 | system/user.vue | ✅ |
| POST | /api/v1/admin/users/{user_id}/reset-password | 重置密码 | system/user.vue | ✅ |
| GET | /api/v1/admin/roles | 获取角色列表 | system/role.vue | ✅ |
| POST | /api/v1/admin/roles | 创建角色 | system/role.vue | ✅ |
| GET | /api/v1/admin/roles/{role_id} | 获取角色详情 | system/role.vue | ✅ |
| PUT | /api/v1/admin/roles/{role_id} | 更新角色 | system/role.vue | ✅ |
| DELETE | /api/v1/admin/roles/{role_id} | 删除角色 | system/role.vue | ✅ |
| GET | /api/v1/admin/permissions | 获取权限列表 | system/role.vue | ✅ |
| GET | /api/v1/admin/menu | 获取菜单树 | - | ❌ |
| POST | /api/v1/admin/menu | 创建菜单 | - | ❌ |
| GET | /api/v1/admin/menu/{menu_id} | 获取菜单详情 | - | ❌ |
| PUT | /api/v1/admin/menu/{menu_id} | 更新菜单 | - | ❌ |
| DELETE | /api/v1/admin/menu/{menu_id} | 删除菜单 | - | ❌ |
| GET | /api/v1/admin/config | 获取系统配置 | system/config.vue | ✅ |
| PUT | /api/v1/admin/config/{config_key} | 更新系统配置 | system/config.vue | ✅ |
| GET | /api/v1/admin/dict | 获取字典类型列表 | system/dict.vue | ✅ |
| POST | /api/v1/admin/dict | 创建字典类型 | system/dict.vue | ✅ |
| GET | /api/v1/admin/dict/{type_id} | 获取字典类型详情 | system/dict.vue | ✅ |
| PUT | /api/v1/admin/dict/{type_id} | 更新字典类型 | system/dict.vue | ✅ |
| DELETE | /api/v1/admin/dict/{type_id} | 删除字典类型 | system/dict.vue | ✅ |
| GET | /api/v1/admin/dict/{type_code}/items | 根据类型获取字典项 | system/dict.vue | ✅ |
| POST | /api/v1/admin/dict/all-items | 创建字典项 | system/dict.vue | ✅ |
| GET | /api/v1/admin/dict/all-items | 获取字典项列表 | system/dict.vue | ✅ |
| GET | /api/v1/admin/dict/items/{item_id} | 获取字典项详情 | system/dict.vue | ✅ |
| PUT | /api/v1/admin/dict/items/{item_id} | 更新字典项 | system/dict.vue | ✅ |
| DELETE | /api/v1/admin/dict/items/{item_id} | 删除字典项 | system/dict.vue | ✅ |
| POST | /api/v1/admin/dict/init | 初始化默认字典数据 | - | ❌ |
| GET | /api/v1/admin/backups | 获取备份列表 | backup/list.vue | ✅ |
| POST | /api/v1/admin/backups | 创建备份 | backup/list.vue | ✅ |
| GET | /api/v1/admin/backups/{backup_id} | 获取备份详情 | backup/restore.vue | ✅ |
| POST | /api/v1/admin/backups/{backup_id}/restore | 恢复备份 | backup/restore.vue | ✅ |
| DELETE | /api/v1/admin/backups/{backup_id} | 删除备份 | backup/list.vue | ✅ |
| POST | /api/v1/admin/backups/cleanup | 清理过期备份 | - | ❌ |
| GET | /api/v1/admin/backup | 获取备份列表(别名) | - | ❌ |
| POST | /api/v1/admin/backup | 创建备份(别名) | - | ❌ |
| GET | /api/v1/admin/backup/config | 获取备份配置 | - | ❌ |
| GET | /api/v1/admin/restores | 获取恢复记录列表 | - | ❌ |
| GET | /api/v1/admin/restores/{restore_id} | 获取恢复记录详情 | - | ❌ |
| GET | /api/v1/admin/logs | 获取操作日志 | system/logs.vue | ✅ |
| POST | /api/v1/admin/logs/cleanup | 清理过期日志 | - | ❌ |
| GET | /api/v1/admin/logs/groups | 获取日志归集组列表 | - | ❌ |
| GET | /api/v1/admin/logs/groups/{group_id}/items | 获取归集组内日志明细 | - | ❌ |
| GET | /api/v1/admin/system-logs | 获取系统日志 | - | ❌ |
| GET | /api/v1/admin/log-stats | 获取日志统计 | - | ❌ |
| GET | /api/v1/admin/log-configs | 获取日志配置列表 | - | ❌ |
| PUT | /api/v1/admin/log-configs | 批量更新日志配置 | - | ❌ |
| GET | /api/v1/admin/collection-logs | 获取采集日志 | - | ❌ |
| GET | /api/v1/admin/metrics | 获取系统指标 | - | ❌ |
| GET | /api/v1/admin/departments | 获取部门列表 | - | ❌ |
| POST | /api/v1/admin/departments | 创建部门 | - | ❌ |
| GET | /api/v1/admin/departments/tree | 获取部门树 | - | ❌ |
| GET | /api/v1/admin/departments/{dept_id} | 获取部门详情 | - | ❌ |
| PUT | /api/v1/admin/departments/{dept_id} | 更新部门 | - | ❌ |
| DELETE | /api/v1/admin/departments/{dept_id} | 删除部门 | - | ❌ |
| GET | /api/v1/admin/timezones | 获取可用时区列表 | - | ❌ |
| GET | /api/v1/admin/adapters | 获取适配器列表 | system/adapters.vue | ✅ |
| POST | /api/v1/admin/adapters | 创建适配器模板 | system/adapters.vue | ✅ |
| GET | /api/v1/admin/adapters/{adapter_id} | 获取适配器详情 | system/adapters.vue | ✅ |
| PUT | /api/v1/admin/adapters/{adapter_id} | 更新适配器模板 | system/adapters.vue | ✅ |
| DELETE | /api/v1/admin/adapters/{adapter_id} | 删除适配器模板 | system/adapters.vue | ✅ |
| GET | /api/v1/admin/device/{device_id}/protocols | 获取设备协议 | system/adapters.vue | ✅ |
| PUT | /api/v1/admin/device/{device_id}/protocols | 保存设备协议 | system/adapters.vue | ✅ |
| POST | /api/v1/admin/device/{device_id}/protocols/{protocol_type}/test | 测试设备协议 | system/adapters.vue | ✅ |
| GET | /api/v1/admin/api-keys | 获取API Key列表 | - | ❌ |
| POST | /api/v1/admin/api-keys | 创建API Key | - | ❌ |
| GET | /api/v1/admin/api-keys/{key_id} | 获取API Key详情 | - | ❌ |
| PUT | /api/v1/admin/api-keys/{key_id} | 更新API Key | - | ❌ |
| DELETE | /api/v1/admin/api-keys/{key_id} | 删除API Key | - | ❌ |
| POST | /api/v1/admin/api-keys/{key_id}/activate | 激活API Key | - | ❌ |
| POST | /api/v1/admin/api-keys/{key_id}/revoke | 撤销API Key | - | ❌ |
| POST | /api/v1/admin/api-keys/{key_id}/rotate | 轮换API Key | - | ❌ |
| POST | /api/v1/admin/cache/clear | 清空缓存 | - | ❌ |
| POST | /api/v1/admin/internal/sql | 内部SQL执行 | - | ❌ |

---

### 2.2 监控管理 (monitoring) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/monitoring/alerts | 获取告警列表 | monitoring/alerts.vue | ✅ |
| POST | /api/v1/monitoring/alerts | 创建告警 | - | ❌ |
| GET | /api/v1/monitoring/alerts/stats | 获取告警统计 | monitoring/alerts.vue | ✅ |
| GET | /api/v1/monitoring/alerts/statistics | 获取告警统计(别名) | - | ❌ |
| GET | /api/v1/monitoring/alerts/{alert_id} | 获取告警详情 | monitoring/alerts.vue | ✅ |
| DELETE | /api/v1/monitoring/alerts/{alert_id} | 删除告警 | - | ❌ |
| PUT | /api/v1/monitoring/alerts/{alert_id}/acknowledge | 确认告警 | monitoring/alerts.vue | ✅ |
| PUT | /api/v1/monitoring/alerts/{alert_id}/resolve | 解决告警 | monitoring/alerts.vue | ✅ |
| POST | /api/v1/monitoring/alerts/{alert_id}/suppress | 屏蔽告警 | - | ❌ |
| POST | /api/v1/monitoring/alerts/{alert_id}/transfer | 转派告警 | - | ❌ |
| POST | /api/v1/monitoring/alerts/{alert_id}/restore | 恢复告警 | - | ❌ |
| GET | /api/v1/monitoring/alerts/{alert_id}/audit-logs | 获取告警审计日志 | - | ❌ |
| POST | /api/v1/monitoring/alerts/{alert_id}/audit-logs | 创建告警审计日志 | - | ❌ |
| GET | /api/v1/monitoring/audit-logs | 获取告警审计日志列表 | - | ❌ |
| GET | /api/v1/monitoring/metrics | 查询监控指标 | monitoring/performance.vue | ✅ |
| POST | /api/v1/monitoring/metrics/query | PromQL风格查询 | monitoring/performance.vue | ✅ |
| GET | /api/v1/monitoring/metrics/hosts | 获取已监控主机列表 | - | ❌ |
| GET | /api/v1/monitoring/metrics/available | 获取可用指标列表 | - | ❌ |
| POST | /api/v1/monitoring/metrics/collect | 手动采集设备指标 | - | ❌ |
| GET | /api/v1/monitoring/dashboards | 获取监控仪表盘列表 | - | ❌ |
| GET | /api/v1/monitoring/dashboards/{dashboard_id} | 获取仪表盘配置 | - | ❌ |
| GET | /api/v1/monitoring/dashboard/layout | 获取用户仪表盘布局 | - | ❌ |
| PUT | /api/v1/monitoring/dashboard/layout | 保存用户仪表盘布局 | - | ❌ |
| GET | /api/v1/monitoring/dashboard/layouts | 获取用户所有仪表盘布局 | - | ❌ |
| DELETE | /api/v1/monitoring/dashboard/layout/{layout_id} | 删除仪表盘布局 | - | ❌ |
| POST | /api/v1/monitoring/dashboard/layout/snapshot | 创建布局快照 | - | ❌ |
| GET | /api/v1/monitoring/dashboard/layout/snapshot/{layout_id}/{version} | 获取布局快照 | - | ❌ |
| GET | /api/v1/monitoring/dashboard/columns | 获取仪表盘列配置 | - | ❌ |
| GET | /api/v1/monitoring/dashboard/stats | 获取仪表盘统计数据 | - | ❌ |
| GET | /api/v1/monitoring/maintenance-windows | 获取维护时段列表 | - | ❌ |
| POST | /api/v1/monitoring/maintenance-windows | 创建维护时段 | - | ❌ |
| GET | /api/v1/monitoring/maintenance-windows/{window_id} | 获取维护时段详情 | - | ❌ |
| PUT | /api/v1/monitoring/maintenance-windows/{window_id} | 更新维护时段 | - | ❌ |
| DELETE | /api/v1/monitoring/maintenance-windows/{window_id} | 删除维护时段 | - | ❌ |
| GET | /api/v1/monitoring/rules | 获取告警规则列表 | - | ❌ |
| GET | /api/v1/monitoring/rules/{rule_id} | 获取告警规则详情 | - | ❌ |
| GET | /api/v1/monitoring/trigger-rules | 获取触发规则列表 | - | ❌ |
| POST | /api/v1/monitoring/trigger-rules | 创建触发规则 | - | ❌ |
| GET | /api/v1/monitoring/trigger-rules/{rule_id} | 获取触发规则详情 | - | ❌ |
| PUT | /api/v1/monitoring/trigger-rules/{rule_id} | 更新触发规则 | - | ❌ |
| DELETE | /api/v1/monitoring/trigger-rules/{rule_id} | 删除触发规则 | - | ❌ |
| POST | /api/v1/monitoring/trigger-rules/{rule_id}/test | 测试触发规则 | - | ❌ |
| GET | /api/v1/monitoring/trigger-events | 获取触发事件列表 | - | ❌ |
| POST | /api/v1/monitoring/trigger/evaluate | 评估指标触发条件 | - | ❌ |
| GET | /api/v1/monitoring/metric-configs | 获取设备采集项配置列表 | - | ❌ |
| POST | /api/v1/monitoring/metric-configs | 创建设备采集项配置 | - | ❌ |
| GET | /api/v1/monitoring/metric-configs/{config_id} | 获取采集项配置详情 | - | ❌ |
| PATCH | /api/v1/monitoring/metric-configs/{config_id} | 更新采集项配置 | - | ❌ |
| DELETE | /api/v1/monitoring/metric-configs/{config_id} | 删除采集项配置 | - | ❌ |
| PATCH | /api/v1/monitoring/metric-configs/{config_id}/toggle | 切换采集项开关 | - | ❌ |
| GET | /api/v1/monitoring/metric-configs/device/{device_id} | 获取设备的所有采集项配置 | - | ❌ |

---

### 2.3 设备管理 (devices) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/devices | 获取设备列表 | - | ❌ |
| GET | /api/v1/devices/{device_name} | 获取设备详情 | - | ❌ |
| GET | /api/v1/devices/{device_name}/status | 获取设备状态 | - | ❌ |
| GET | /api/v1/devices/{device_name}/metrics | 获取设备指标 | - | ❌ |
| GET | /api/v1/devices/{device_name}/metrics/history | 获取设备指标历史 | - | ❌ |
| GET | /api/v1/devices/{device_name}/collection-config | 获取设备采集配置 | - | ❌ |
| PATCH | /api/v1/devices/{device_name}/collection-config | 更新设备采集配置 | - | ❌ |
| GET | /api/v1/devices/{device_id}/metrics | 获取设备所有指标配置 | - | ❌ |
| PATCH | /api/v1/devices/{device_id}/metrics | 更新设备指标配置 | - | ❌ |
| POST | /api/v1/devices/{device_id}/metrics/bulk | 批量更新设备指标配置 | - | ❌ |
| GET | /api/v1/devices/{device_id}/metrics/categories | 获取设备指标类别 | - | ❌ |
| GET | /api/v1/devices/{device_id}/metrics/configs | 获取设备所有指标配置 | - | ❌ |
| GET | /api/v1/devices/{device_id}/metrics/{metric}/config | 获取设备指标配置 | - | ❌ |
| PATCH | /api/v1/devices/{device_id}/metrics/{metric} | 更新设备指标采集配置 | - | ❌ |
| GET | /api/v1/devices/name/{device_name}/metrics | 通过设备名获取指标配置 | - | ❌ |
| PATCH | /api/v1/devices/name/{device_name}/metrics | 通过设备名更新指标配置 | - | ❌ |
| GET | /api/v1/devices/stats | 获取设备统计 | - | ❌ |
| POST | /api/v1/devices/collect | 采集设备指标 | - | ❌ |
| POST | /api/v1/devices/collect/all | 采集所有设备 | - | ❌ |
| GET | /api/v1/devices/config/stats | 获取配置统计 | - | ❌ |
| POST | /api/v1/devices/config/reload | 重新加载配置 | - | ❌ |
| GET | /api/v1/devices/adapters/list | 获取支持的适配器列表 | - | ❌ |
| GET | /api/v1/devices/adapters/protocols | 获取支持的协议列表 | - | ❌ |
| POST | /api/v1/devices/import | 批量导入设备 | - | ❌ |
| POST | /api/v1/devices/import/simple | 简单批量导入 | - | ❌ |
| GET | /api/v1/devices/import/template | 下载设备导入模板 | - | ❌ |
| POST | /api/v1/devices/import/validate | 验证导入数据 | - | ❌ |

---

### 2.4 资产管理 (assets) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/assets/device | 获取设备列表 | monitoring/performance.vue, automation/task.vue, system/adapters.vue | ✅ |
| POST | /api/v1/assets/device | 创建设备 | - | ❌ |
| GET | /api/v1/assets/device/{device_id} | 获取设备详情 | - | ❌ |
| PUT | /api/v1/assets/device/{device_id} | 更新设备 | - | ❌ |
| DELETE | /api/v1/assets/device/{device_id} | 删除设备 | - | ❌ |
| POST | /api/v1/assets/device/batch | 批量操作设备 | - | ❌ |
| POST | /api/v1/assets/device/{device_id}/maintain | 设置设备维护状态 | - | ❌ |
| POST | /api/v1/assets/device/{device_id}/decommission | 退役设备 | - | ❌ |
| GET | /api/v1/assets/device/{device_id}/metrics | 获取设备关联指标 | automation/task.vue | ✅ |
| GET | /api/v1/assets/group | 获取设备分组列表 | - | ❌ |
| GET | /api/v1/assets/group/{group_id}/devices | 获取分组下设备列表 | - | ❌ |
| GET | /api/v1/assets/business | 获取业务系统列表 | - | ❌ |
| GET | /api/v1/assets/business/{business_id} | 获取业务系统详情 | - | ❌ |
| GET | /api/v1/assets/business/{business_id}/devices | 获取业务系统关联设备 | - | ❌ |
| GET | /api/v1/assets/config | 获取配置项列表 | - | ❌ |
| PUT | /api/v1/assets/config/{config_id} | 更新配置项 | - | ❌ |
| DELETE | /api/v1/assets/config/{config_id} | 删除配置项 | - | ❌ |
| POST | /api/v1/assets/config/snapshot | 创建设备配置快照 | - | ❌ |
| POST | /api/v1/assets/config/sync/{device_id} | 同步设备配置 | - | ❌ |
| GET | /api/v1/assets/stats | 获取资产统计 | - | ❌ |

---

### 2.5 工单管理 (workorders) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/workorders/ | 获取工单列表 | workorder/list.vue, workorder/my.vue | ✅ |
| POST | /api/v1/workorders/ | 创建工单 | workorder/create.vue | ✅ |
| GET | /api/v1/workorders | 获取工单列表(别名) | - | ❌ |
| GET | /api/v1/workorders/{workorder_id} | 获取工单详情 | - | ❌ |
| PUT | /api/v1/workorders/{workorder_id} | 更新工单 | - | ❌ |
| DELETE | /api/v1/workorders/{workorder_id} | 删除工单 | - | ❌ |
| POST | /api/v1/workorders/{workorder_id}/assign | 分配工单 | - | ❌ |
| POST | /api/v1/workorders/{workorder_id}/approve | 审批工单 | - | ❌ |
| POST | /api/v1/workorders/{workorder_id}/resolve | 解决工单 | - | ❌ |
| POST | /api/v1/workorders/{workorder_id}/close | 关闭工单 | - | ❌ |
| POST | /api/v1/workorders/{workorder_id}/cancel | 取消工单 | - | ❌ |
| GET | /api/v1/workorders/{workorder_id}/flows | 获取工单流程历史 | - | ❌ |
| POST | /api/v1/workorders/{workorder_id}/flows | 添加工单流程记录 | - | ❌ |
| GET | /api/v1/workorders/{workorder_id}/approval-flow | 获取工单审批流程图 | - | ❌ |
| GET | /api/v1/workorders/{workorder_id}/draft | 获取工单草稿 | - | ❌ |
| PUT | /api/v1/workorders/{workorder_id}/draft | 保存工单草稿 | - | ❌ |
| GET | /api/v1/workorders/categories | 获取工单分类列表 | - | ❌ |
| GET | /api/v1/workorders/priorities | 获取工单优先级列表 | - | ❌ |
| GET | /api/v1/workorders/stats/summary | 获取工单统计摘要 | - | ❌ |
| GET | /api/v1/workorders/stats/trend | 获取工单趋势 | - | ❌ |
| GET | /api/v1/workorders/export | 导出工单 | - | ❌ |
| GET | /api/v1/workorders/export/{workorder_id} | 导出单个工单 | - | ❌ |
| GET | /api/v1/workorders/sla/summary | 获取SLA汇总 | - | ❌ |
| GET | /api/v1/workorders/sla/{workorder_id} | 获取SLA状态 | - | ❌ |
| POST | /api/v1/workorders/sla/{workorder_id}/start | 启动SLA计时 | - | ❌ |
| GET | /api/v1/workorders/{workorder_id}/sla | 获取工单SLA状态 | - | ❌ |
| GET | /api/v1/workorders/{workorder_id}/sla/history | 获取SLA升级历史 | - | ❌ |
| POST | /api/v1/workorders/{workorder_id}/sla/refresh | 刷新SLA状态 | - | ❌ |
| POST | /api/v1/workorders/{workorder_id}/sla/timer/start | 启动SLA计时器 | - | ❌ |
| GET | /api/v1/workorders/draft/list | 获取草稿列表 | - | ❌ |
| POST | /api/v1/workorders/draft/save | 保存工单草稿 | - | ❌ |
| GET | /api/v1/workorders/draft/{draft_id} | 获取草稿详情 | - | ❌ |
| DELETE | /api/v1/workorders/draft/{draft_id} | 删除草稿 | - | ❌ |
| POST | /api/v1/workorders/analyze/remediation | AI修复建议 | - | ❌ |
| POST | /api/v1/workorders/analyze/root-cause | AI根因分析 | - | ❌ |

---

### 2.6 知识库 (knowledge) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/knowledge/category | 获取分类列表 | ai/copilot.vue, knowledge/list.vue | ✅ |
| POST | /api/v1/knowledge/category | 创建分类 | ai/copilot.vue | ✅ |
| GET | /api/v1/knowledge/sop | 获取SOP文档列表 | ai/copilot.vue, knowledge/list.vue | ✅ |
| POST | /api/v1/knowledge/sop | 创建SOP文档 | knowledge/list.vue | ✅ |
| GET | /api/v1/knowledge/sop/{doc_id} | 获取SOP文档详情 | knowledge/list.vue | ✅ |
| PUT | /api/v1/knowledge/sop/{doc_id} | 更新SOP文档 | knowledge/list.vue | ✅ |
| DELETE | /api/v1/knowledge/sop/{doc_id} | 删除SOP文档 | knowledge/list.vue | ✅ |
| POST | /api/v1/knowledge/sop/{doc_id}/review | 提交SOP文档审核 | knowledge/list.vue | ✅ |
| POST | /api/v1/knowledge/sop/{doc_id}/approve | 批准SOP文档 | knowledge/list.vue | ✅ |
| GET | /api/v1/knowledge/fault-case | 获取故障案例列表 | knowledge/cases.vue | ✅ |
| POST | /api/v1/knowledge/fault-case | 创建故障案例 | - | ❌ |
| GET | /api/v1/knowledge/fault-case/{case_id} | 获取故障案例详情 | - | ❌ |
| PUT | /api/v1/knowledge/fault-case/{case_id} | 更新故障案例 | - | ❌ |
| POST | /api/v1/knowledge/fault-case/{case_id}/recommend-similar | AI推荐相似故障案例 | - | ❌ |
| GET | /api/v1/knowledge/search | 知识库搜索 | - | ❌ |
| GET | /api/v1/knowledge/stats | 获取知识库统计 | - | ❌ |
| GET | /api/v1/knowledge/tag | 获取标签列表 | - | ❌ |
| POST | /api/v1/knowledge/tag | 创建标签 | - | ❌ |
| GET | /api/v1/knowledge/review-flows | 获取审核流程列表 | - | ❌ |
| POST | /api/v1/knowledge/review-flows | 创建审核流程 | - | ❌ |
| GET | /api/v1/knowledge/review-flows/{flow_id} | 获取审核流程详情 | - | ❌ |
| PUT | /api/v1/knowledge/review-flows/{flow_id} | 更新审核流程 | - | ❌ |
| DELETE | /api/v1/knowledge/review-flows/{flow_id} | 删除审核流程 | - | ❌ |
| GET | /api/v1/knowledge/reviews | 获取审核记录列表 | - | ❌ |
| GET | /api/v1/knowledge/reviews/pending | 获取待审核列表 | - | ❌ |
| GET | /api/v1/knowledge/reviews/{review_id} | 获取审核记录详情 | - | ❌ |
| POST | /api/v1/knowledge/reviews/submit | 提交文档审核 | - | ❌ |
| POST | /api/v1/knowledge/reviews/{review_id}/approve | 批准审核 | - | ❌ |
| POST | /api/v1/knowledge/reviews/{review_id}/reject | 拒绝审核 | - | ❌ |
| POST | /api/v1/knowledge/reviews/{review_id}/request-revision | 要求修订 | - | ❌ |
| POST | /api/v1/knowledge/reviews/{review_id}/resubmit | 重新提交审核 | - | ❌ |
| POST | /api/v1/knowledge/reviews/{review_id}/withdraw | 撤回审核 | - | ❌ |
| GET | /api/v1/knowledge/graph/nodes | 查询图节点 | - | ❌ |
| POST | /api/v1/knowledge/graph/nodes | 创建图节点 | - | ❌ |
| GET | /api/v1/knowledge/graph/stats | 图谱统计 | - | ❌ |
| POST | /api/v1/knowledge/graph/build | 构建筑识图谱 | - | ❌ |
| GET | /api/v1/knowledge/graph/case/{case_id}/context | 案例图谱上下文 | - | ❌ |
| GET | /api/v1/knowledge/graph/case/{case_id}/similar | 图谱相似案例查询 | - | ❌ |
| GET | /api/v1/knowledge/graph/path/{case_a_id}/{case_b_id} | 两案例关联路径 | - | ❌ |
| POST | /api/v1/knowledge/graph/relationships | 创建图关系 | - | ❌ |

---

### 2.7 自动化 (automation) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/automation/trigger-rules | 列出触发规则 | automation/script.vue | ✅ |
| POST | /api/v1/automation/trigger-rules | 创建触发规则 | automation/script.vue | ✅ |
| GET | /api/v1/automation/trigger-rules/{rule_id} | 获取触发规则 | automation/script.vue | ✅ |
| PUT | /api/v1/automation/trigger-rules/{rule_id} | 更新触发规则 | automation/script.vue | ✅ |
| DELETE | /api/v1/automation/trigger-rules/{rule_id} | 删除触发规则 | automation/script.vue | ✅ |
| POST | /api/v1/automation/trigger-rules/{rule_id}/test | 测试触发规则 | automation/script.vue | ✅ |
| GET | /api/v1/automation/scripts | 获取脚本列表 | - | ❌ |
| POST | /api/v1/automation/scripts | 创建脚本 | - | ❌ |
| GET | /api/v1/automation/scripts/{script_id} | 获取脚本详情 | - | ❌ |
| PUT | /api/v1/automation/scripts/{script_id} | 更新脚本 | - | ❌ |
| DELETE | /api/v1/automation/scripts/{script_id} | 删除脚本 | - | ❌ |
| POST | /api/v1/automation/scripts/{script_id}/execute | 立即执行脚本 | - | ❌ |
| GET | /api/v1/automation/scripts/{script_id}/versions | 获取脚本版本历史 | - | ❌ |
| GET | /api/v1/automation/tasks | 获取任务列表 | automation/task.vue | ✅ |
| POST | /api/v1/automation/tasks | 创建任务 | automation/task.vue | ✅ |
| GET | /api/v1/automation/tasks/{task_id} | 获取任务详情 | automation/task.vue | ✅ |
| PUT | /api/v1/automation/tasks/{task_id} | 更新任务 | automation/task.vue | ✅ |
| DELETE | /api/v1/automation/tasks/{task_id} | 删除任务 | automation/task.vue | ✅ |
| POST | /api/v1/automation/tasks/{task_id}/run | 立即执行任务 | automation/task.vue | ✅ |
| GET | /api/v1/automation/executions | 获取执行记录列表 | automation/task.vue | ✅ |
| GET | /api/v1/automation/executions/{execution_id} | 获取执行详情 | - | ❌ |
| GET | /api/v1/automation/executions/{execution_id}/logs | 获取执行日志 | - | ❌ |
| GET | /api/v1/automation/executions/{execution_id}/snapshot | 获取快照 | automation/task.vue, automation/execute.vue | ✅ |
| POST | /api/v1/automation/executions/{execution_id}/rollback | 执行回滚 | - | ❌ |
| GET | /api/v1/automation/rollback-history | 获取回滚历史 | automation/task.vue, automation/execute.vue | ✅ |
| POST | /api/v1/automation/evaluate | 评估指标是否超阈值 | automation/task.vue | ✅ |
| POST | /api/v1/automation/events | 触发自动化事件 | - | ❌ |

---

### 2.8 AI 助手 (ai) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| POST | /api/v1/ai/chat | 发送消息 | ai/chat.vue | ✅ |
| GET | /api/v1/ai/conversations | 获取会话列表 | ai/chat.vue | ✅ |
| GET | /api/v1/ai/conversations/{conversation_id} | 获取会话历史 | ai/chat.vue | ✅ |
| DELETE | /api/v1/ai/conversations/{conversation_id} | 删除会话 | - | ❌ |
| PUT | /api/v1/ai/conversations/{conversation_id}/pin | 置顶会话 | ai/chat.vue | ✅ |
| POST | /api/v1/ai/conversations/{conversation_id}/messages | 保存消息到会话 | - | ❌ |
| POST | /api/v1/ai/knowledge-qa | 知识问答 | ai/copilot.vue | ✅ |
| POST | /api/v1/ai/qa | 知识问答(别名) | - | ❌ |
| POST | /api/v1/ai/troubleshoot | 智能故障排查 | ai/analyze.vue | ✅ |
| POST | /api/v1/ai/troubleshoot/auto | 自动故障诊断 | - | ❌ |
| POST | /api/v1/ai/analyze/{alert_id}/root-cause | alert根因分析 | - | ❌ |
| POST | /api/v1/ai/analyze/{alert_id}/remediation | alert智能处置 | - | ❌ |
| POST | /api/v1/ai/analyze/logs | 分析日志 | - | ❌ |
| POST | /api/v1/ai/interpret/report | 解读报表 | - | ❌ |
| POST | /api/v1/ai/suggest | 生成优化建议 | - | ❌ |
| GET | /api/v1/ai/stats | 获取AI助手统计 | - | ❌ |
| POST | /api/v1/ai/chat/_debug | debug流式接口 | - | ❌ |

---

### 2.9 认证 (auth) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| POST | /api/v1/auth/login | 登录 | - | ❌ |
| POST | /api/v1/auth/logout | 登出 | - | ❌ |
| POST | /api/v1/auth/refresh | 刷新Token | - | ❌ |
| GET | /api/v1/auth/userinfo | 获取用户信息 | - | ❌ |
| GET | /api/v1/auth/captcha | 获取验证码 | - | ❌ |
| POST | /api/v1/auth/register | 注册 | - | ❌ |
| PUT | /api/v1/auth/password | 修改密码 | - | ❌ |
| POST | /api/v1/auth/change-password-first-login | 首次登录修改密码 | - | ❌ |
| POST | /api/v1/auth/ldap-login | LDAP登录 | - | ❌ |
| GET | /api/v1/auth/ldap/status | LDAP状态 | - | ❌ |

---

### 2.10 通知 (notifications) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/notifications/channels | 获取通知渠道 | notification/config.vue | ✅ |
| POST | /api/v1/notifications/channels | 创建通知渠道 | notification/config.vue | ✅ |
| GET | /api/v1/notifications/channels/{channel_id} | 获取单个渠道 | notification/config.vue | ✅ |
| PUT | /api/v1/notifications/channels/{channel_id} | 更新通知渠道 | notification/config.vue | ✅ |
| DELETE | /api/v1/notifications/channels/{channel_id} | 删除通知渠道 | notification/config.vue | ✅ |
| POST | /api/v1/notifications/test/{channel_id} | 测试通知渠道 | notification/config.vue | ✅ |
| GET | /api/v1/notifications/types | 获取通知类型列表 | notification/config.vue | ✅ |
| GET | /api/v1/notifications/history | 获取通知历史 | notification/history.vue, notification/message.vue | ✅ |
| PUT | /api/v1/notifications/history/read-all | 标记全部已读 | notification/history.vue, notification/message.vue | ✅ |
| GET | /api/v1/notifications/history/{log_id}/read | 标记单条已读 | notification/history.vue | ✅ |
| GET | /api/v1/notifications/messages | 获取站内消息列表 | notification/message.vue | ✅ |
| POST | /api/v1/notifications/messages | 创建站内消息 | - | ❌ |
| PUT | /api/v1/notifications/messages/read-all | 标记全部消息已读 | notification/message.vue | ✅ |
| PUT | /api/v1/notifications/messages/{message_id}/read | 标记消息已读 | notification/message.vue | ✅ |
| DELETE | /api/v1/notifications/messages/{message_id} | 删除消息 | - | ❌ |
| GET | /api/v1/notifications/messages/unread-count | 获取未读消息数量 | - | ❌ |
| GET | /api/v1/notifications/targets | 获取通知对象配置列表 | - | ❌ |
| POST | /api/v1/notifications/targets | 创建通知对象配置 | - | ❌ |
| GET | /api/v1/notifications/targets/{target_id} | 获取通知对象配置详情 | - | ❌ |
| DELETE | /api/v1/notifications/targets/{target_id} | 删除通知对象配置 | - | ❌ |
| GET | /api/v1/notifications/target-rules | 获取通知目标规则列表 | - | ❌ |
| POST | /api/v1/notifications/target-rules | 创建通知目标规则 | - | ❌ |
| GET | /api/v1/notifications/target-rules/{rule_id} | 获取通知目标规则详情 | - | ❌ |
| PUT | /api/v1/notifications/target-rules/{rule_id} | 更新通知目标规则 | - | ❌ |
| DELETE | /api/v1/notifications/target-rules/{rule_id} | 删除通知目标规则 | - | ❌ |
| POST | /api/v1/notifications/target-rules/{rule_id}/toggle | 启用/禁用规则 | - | ❌ |
| GET | /api/v1/notifications/target-rules/match | 匹配通知目标规则 | - | ❌ |
| POST | /api/v1/notifications/send | 发送通知 | - | ❌ |
| POST | /api/v1/notifications/alert | 发送告警通知 | - | ❌ |

---

### 2.11 报表 (reports) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/reports/ | 获取报表列表 | report/list.vue | ✅ |
| GET | /api/v1/reports | 获取报表列表(别名) | report/list.vue | ✅ |
| GET | /api/v1/reports/{report_id} | 获取报表详情 | report/list.vue | ✅ |
| DELETE | /api/v1/reports/{report_id} | 删除报表 | report/list.vue | ✅ |
| GET | /api/v1/reports/{report_id}/download | 下载报表 | report/list.vue | ✅ |
| GET | /api/v1/reports/{report_id}/preview | 预览报表 | report/list.vue | ✅ |
| GET | /api/v1/reports/list | 获取报表列表 | - | ❌ |
| POST | /api/v1/reports/generate | 生成报表 | report/create.vue | ✅ |
| POST | /api/v1/reports/generate/async | 异步生成报表 | - | ❌ |
| GET | /api/v1/reports/files/{filename} | 获取报表文件 | - | ❌ |
| GET | /api/v1/reports/stats | 获取报表统计 | report/list.vue | ✅ |
| GET | /api/v1/reports/schedule | 获取定时报表列表 | - | ❌ |
| POST | /api/v1/reports/schedule | 创建定时报表 | - | ❌ |
| PUT | /api/v1/reports/schedule/{schedule_id} | 更新定时报表 | - | ❌ |
| DELETE | /api/v1/reports/schedule/{schedule_id} | 删除定时报表 | - | ❌ |
| POST | /api/v1/reports/schedule/{schedule_id}/toggle | 启用/禁用定时报表 | - | ❌ |
| GET | /api/v1/reports/template | 获取报表模板列表 | report/template.vue, report/create.vue | ✅ |
| POST | /api/v1/reports/template | 创建报表模板 | report/template.vue | ✅ |
| GET | /api/v1/reports/template/{template_id} | 获取报表模板详情 | report/template.vue | ✅ |
| PUT | /api/v1/reports/template/{template_id} | 更新报表模板 | report/template.vue | ✅ |
| DELETE | /api/v1/reports/template/{template_id} | 删除报表模板 | report/template.vue | ✅ |
| GET | /api/v1/report | 获取报表列表(单数别名) | - | ❌ |
| POST | /api/v1/reports/preview | 预览报表内容 | report/create.vue | ✅ |

---

### 2.12 巡检 (inspection) - 标注: ❌未对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/inspection/tasks | 获取巡检任务列表 | - | ❌ |
| POST | /api/v1/inspection/tasks | 创建巡检任务 | - | ❌ |
| GET | /api/v1/inspection/tasks/{task_id} | 获取巡检任务详情 | - | ❌ |
| PUT | /api/v1/inspection/tasks/{task_id} | 更新巡检任务 | - | ❌ |
| DELETE | /api/v1/inspection/tasks/{task_id} | 删除巡检任务 | - | ❌ |
| GET | /api/v1/inspection/results/{task_id} | 获取巡检结果列表 | - | ❌ |
| GET | /api/v1/inspection/reports/{task_id} | 获取巡检报告 | - | ❌ |
| GET | /api/v1/inspection/reports/template | 获取巡检报告模板 | - | ❌ |
| GET | /api/v1/inspection/reports/{task_id}/export | 导出巡检报告 | - | ❌ |
| GET | /api/v1/inspection/statistics/summary | 获取巡检统计摘要 | - | ❌ |

---

### 2.13 部署 (deploy) - 标注: ❌未对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/deploy/versions | 列出版本列表 | - | ❌ |
| POST | /api/v1/deploy/versions | 注册版本 | - | ❌ |
| GET | /api/v1/deploy/versions/{name} | 获取版本详情 | - | ❌ |
| DELETE | /api/v1/deploy/versions/{name} | 删除版本 | - | ❌ |
| GET | /api/v1/deploy/canary | 列表金丝雀 | - | ❌ |
| POST | /api/v1/deploy/canary | 创建金丝雀 | - | ❌ |
| GET | /api/v1/deploy/canary/{canary_id} | 获取金丝雀详情 | - | ❌ |
| DELETE | /api/v1/deploy/canary/{canary_id} | 终止金丝雀 | - | ❌ |
| POST | /api/v1/deploy/canary/{canary_id}/promote | 提升金丝雀 | - | ❌ |
| POST | /api/v1/deploy/canary/{canary_id}/rollback | 回滚金丝雀 | - | ❌ |
| PUT | /api/v1/deploy/canary/{canary_id}/weight | 更新金丝雀权重 | - | ❌ |
| GET | /api/v1/deploy/history | 部署历史 | - | ❌ |
| GET | /api/v1/deploy/status | 部署状态 | - | ❌ |
| GET | /api/v1/deploy/health | 部署健康状态 | - | ❌ |

---

### 2.14 设备发现 (discovery) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/discovery/networks | 获取已配置网段列表 | discovery/scan.vue | ✅ |
| POST | /api/v1/discovery/networks | 添加扫描网段 | discovery/scan.vue | ✅ |
| GET | /api/v1/discovery/networks/{network_id} | 获取网段详情 | discovery/scan.vue | ✅ |
| PUT | /api/v1/discovery/networks/{network_id} | 更新扫描网段 | discovery/scan.vue | ✅ |
| DELETE | /api/v1/discovery/networks/{network_id} | 删除扫描网段 | discovery/scan.vue | ✅ |
| POST | /api/v1/discovery/scan | 启动设备扫描 | - | ❌ |
| POST | /api/v1/discovery/scan-and-import | 扫描并自动导入 | discovery/scan.vue | ✅ |
| POST | /api/v1/discovery/scan-and-import-stream | 启动扫描(轮询) | discovery/scan.vue | ✅ |
| GET | /api/v1/discovery/scan-and-import-stream/{scan_id} | 查询扫描进度 | discovery/scan.vue | ✅ |
| GET | /api/v1/discovery/scan-history | 获取扫描历史列表 | discovery/scan.vue | ✅ |
| GET | /api/v1/discovery/scan/{task_id}/status | 获取扫描任务状态 | - | ❌ |
| POST | /api/v1/discovery/import | 导入发现的主机 | discovery/scan.vue | ✅ |
| GET | /api/v1/discovery/hosts | 获取发现的主机列表 | - | ❌ |
| POST | /api/v1/discovery/ip/scan | 启动IP范围扫描 | - | ❌ |
| POST | /api/v1/discovery/ip/scan/sync | 同步IP范围扫描 | - | ❌ |
| GET | /api/v1/discovery/ip/scan/{task_id}/results | 获取IP扫描结果 | - | ❌ |
| GET | /api/v1/discovery/ip/hosts | 获取IP扫描发现的主机 | - | ❌ |
| POST | /api/v1/discovery/arp/scan | ARP扫描网段 | - | ❌ |
| GET | /api/v1/discovery/tasks | 获取发现任务列表 | - | ❌ |
| POST | /api/v1/discovery/tasks | 创建设备发现任务 | - | ❌ |
| POST | /api/v1/discovery/snmp/scan | 启动SNMP扫描 | - | ❌ |
| POST | /api/v1/discovery/snmp/scan/sync | 同步SNMP扫描 | - | ❌ |
| GET | /api/v1/discovery/snmp/scan/{task_id}/results | 获取SNMP扫描结果 | - | ❌ |
| POST | /api/v1/discovery/snmp/discover | SNMP设备发现 | - | ❌ |
| GET | /api/v1/discovery/snmp/devices | 获取SNMP设备列表 | - | ❌ |

---

### 2.15 厂商账密 (credentials) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/credentials/vendors | 获取所有厂商列表 | management/VendorCredentials.vue | ✅ |
| POST | /api/v1/credentials/vendors | 新增厂商 | management/VendorCredentials.vue | ✅ |
| GET | /api/v1/credentials/vendors/{vendor_name} | 获取厂商详情 | management/VendorCredentials.vue | ✅ |
| PUT | /api/v1/credentials/vendors/{vendor_name} | 更新厂商 | management/VendorCredentials.vue | ✅ |
| DELETE | /api/v1/credentials/vendors/{vendor_name} | 删除厂商 | management/VendorCredentials.vue | ✅ |
| GET | /api/v1/credentials/vendors/categories | 获取所有分类 | management/VendorCredentials.vue | ✅ |
| GET | /api/v1/credentials/vendors/common-creds | 获取通用默认账密 | management/VendorCredentials.vue | ✅ |
| GET | /api/v1/credentials/versions | 列出版本列表 | - | ❌ |
| POST | /api/v1/credentials/versions | 创建版本快照 | - | ❌ |
| GET | /api/v1/credentials/versions/{version} | 获取指定版本内容 | - | ❌ |
| POST | /api/v1/credentials/versions/{version}/rollback | 回滚到指定版本 | - | ❌ |
| GET | /api/v1/credentials/probe/banner | 根据banner匹配厂商 | - | ❌ |
| GET | /api/v1/credentials/probe/mac | 根据MAC OUI匹配厂商 | - | ❌ |
| GET | /api/v1/credentials/probe/oid | 根据OID匹配厂商 | - | ❌ |

---

### 2.16 系统适配 (system) - 标注: ⚠️部分对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/system/menus | 获取前端菜单树 | system/menu.vue | ✅ |
| POST | /api/v1/system/menus | 创建菜单 | system/menu.vue | ✅ |
| PUT | /api/v1/system/menus/{menu_key} | 更新菜单 | system/menu.vue | ✅ |
| DELETE | /api/v1/system/menus/{menu_key} | 删除菜单 | system/menu.vue | ✅ |

---

### 2.17 API密钥 (api-keys) - 标注: ❌未对接

| 方法 | 路径 | 摘要 | 前端页面 | 状态 |
|------|------|------|----------|------|
| GET | /api/v1/api-keys | 获取API Key列表 | - | ❌ |
| POST | /api/v1/api-keys | 创建API Key | - | ❌ |
| GET | /api/v1/api-keys/{key_id} | 获取API Key详情 | - | ❌ |
| PUT | /api/v1/api-keys/{key_id} | 更新API Key | - | ❌ |
| DELETE | /api/v1/api-keys/{key_id} | 删除API Key | - | ❌ |
| POST | /api/v1/api-keys/{key_id}/activate | 激活API Key | - | ❌ |
| POST | /api/v1/api-keys/{key_id}/revoke | 撤销API Key | - | ❌ |
| POST | /api/v1/api-keys/{key_id}/rotate | 轮换API Key | - | ❌ |

---

### 2.18 其他 - 标注: ❌未对接

| 方法 | 路径 | 摘要 | 模块 | 状态 |
|------|------|------|------|------|
| GET | /api/v1/tenants | 获取租户列表 | 租户管理 | ❌ |
| POST | /api/v1/tenants | 创建租户 | 租户管理 | ❌ |
| GET | /api/v1/tenants/{tenant_id} | 获取租户详情 | 租户管理 | ❌ |
| PUT | /api/v1/tenants/{tenant_id} | 更新租户 | 租户管理 | ❌ |
| DELETE | /api/v1/tenants/{tenant_id} | 删除租户 | 租户管理 | ❌ |
| GET | /api/v1/tenants/{tenant_id}/users | 获取租户下用户列表 | 租户管理 | ❌ |
| POST | /api/v1/tenants/{tenant_id}/users | 将用户分配到租户 | 租户管理 | ❌ |
| DELETE | /api/v1/tenants/{tenant_id}/users/{user_id} | 将用户从租户移除 | 租户管理 | ❌ |
| GET | /api/v1/tenants/{tenant_id}/quota | 获取租户配额使用情况 | 租户管理 | ❌ |
| GET | /api/v1/sharding/stats | 获取分片统计 | 分片管理 | ❌ |
| GET | /api/v1/sharding/routes/{logical_table} | 获取分片路由 | 分片管理 | ❌ |
| POST | /api/v1/sharding/routes/{logical_table}/create | 创建分片 | 分片管理 | ❌ |
| POST | /api/v1/watermark/generate | 生成水印 | 操作水印 | ❌ |
| GET | /api/v1/watermark/list | 列出水印 | 操作水印 | ❌ |
| POST | /api/v1/watermark/log | 记录水印操作 | 操作水印 | ❌ |
| GET | /api/v1/watermark/track/{watermark_id} | 追踪水印 | 操作水印 | ❌ |
| POST | /api/v1/watermark/verify | 验证水印 | 操作水印 | ❌ |

---

## 三、前端对接情况总览

### 3.1 已对接的前端页面和API

| 前端页面 | 调用的API模块 |
|----------|-------------|
| App.vue | /api/v1/admin/info |
| system/user.vue | admin/users, admin/roles |
| system/role.vue | admin/roles, admin/permissions |
| system/menu.vue | system/menus |
| system/config.vue | admin/config |
| system/dict.vue | admin/dict |
| system/logs.vue | admin/logs |
| system/adapters.vue | admin/adapters, assets/device |
| backup/list.vue | admin/backups |
| backup/restore.vue | admin/backups |
| monitoring/alerts.vue | monitoring/alerts |
| monitoring/performance.vue | assets/device, monitoring/metrics/query |
| notification/config.vue | notifications/channels, notifications/types |
| notification/history.vue | notifications/history |
| notification/message.vue | notifications/history, notifications/messages |
| workorder/list.vue | workorders |
| workorder/my.vue | workorders |
| workorder/create.vue | workorders, assets/device |
| automation/task.vue | automation/tasks, automation/trigger-rules, automation/executions, assets/device |
| automation/script.vue | automation/trigger-rules |
| automation/execute.vue | automation/executions, rollback-history |
| knowledge/list.vue | knowledge/sop, knowledge/category |
| knowledge/cases.vue | knowledge/fault-case |
| ai/chat.vue | ai/chat, ai/conversations |
| ai/copilot.vue | ai/knowledge-qa, knowledge/category, knowledge/sop |
| ai/analyze.vue | ai/troubleshoot |
| report/list.vue | reports, reports/stats |
| report/create.vue | reports/generate, reports/template, reports/preview |
| report/template.vue | reports/template |
| discovery/scan.vue | discovery/networks, discovery/scan-and-import, discovery/import |
| management/VendorCredentials.vue | credentials/vendors |

### 3.2 未对接/待完善模块

以下模块API存在但前端未对接：
- **监控管理** (monitoring): 仪表盘、维护时段、触发规则、采集配置
- **设备管理** (devices): 设备详情、指标、采集控制
- **资产管理** (assets): 业务系统、配置项、分组
- **工单管理** (workorders): 审批流程、SLA、草稿、导出
- **知识库** (knowledge): 图谱、故障案例详情、审核流程
- **AI助手** (ai): 根因分析、智能处置、报表解读
- **自动化** (automation): 脚本管理、执行详情
- **报表** (reports): 定时任务、异步生成
- **巡检** (inspection): 全部未对接
- **部署** (deploy): 全部未对接
- **租户管理**: 全部未对接
- **API密钥**: 全部未对接
- **分片管理**: 全部未对接
- **操作水印**: 全部未对接

---

## 四、特别关注: 整体优化要求相关接口

根据API清单，以下是需要重点关注的优化接口：

### 4.1 高频/核心接口（建议优先优化）

| 接口 | 说明 | 当前状态 |
|------|------|----------|
| GET /api/v1/monitoring/alerts | 告警列表查询 | ✅已对接 |
| GET /api/v1/monitoring/metrics/query | PromQL指标查询 | ✅已对接 |
| GET /api/v1/assets/device | 设备列表查询 | ✅已对接 |
| GET /api/v1/knowledge/sop | SOP文档列表 | ✅已对接 |
| GET /api/v1/automation/trigger-rules | 触发规则列表 | ✅已对接 |
| GET /api/v1/workorders/ | 工单列表 | ✅已对接 |
| GET /api/v1/reports/ | 报表列表 | ✅已对接 |

### 4.2 潜在性能问题接口（建议分析优化）

| 接口 | 说明 | 建议 |
|------|------|------|
| GET /api/v1/monitoring/metrics | 时序数据查询 | 检查是否需要分页/采样 |
| GET /api/v1/admin/logs | 日志查询 | 检查是否有索引 |
| GET /api/v1/discovery/snmp/scan/{task_id}/results | SNMP扫描结果 | 大规模环境下可能超时 |
| POST /api/v1/discovery/scan-and-import-stream | 扫描导入 | 建议异步处理 |

### 4.3 安全相关接口（建议审计）

| 接口 | 说明 | 建议 |
|------|------|------|
| POST /api/v1/admin/internal/sql | 内部SQL执行 | ⚠️高危，建议限制IP |
| POST /api/v1/admin/cache/clear | 清空缓存 | ⚠️建议增加确认机制 |
| GET/PUT /api/v1/admin/config | 系统配置 | ⚠️建议权限控制 |

---

## 五、接口统计

| 分类 | 总数 | 已对接 | 未对接 | 对接率 |
|------|------|--------|--------|--------|
| 系统管理 (admin) | ~90 | ~25 | ~65 | 28% |
| 监控管理 (monitoring) | ~35 | ~6 | ~29 | 17% |
| 设备管理 (devices) | ~30 | ~0 | ~30 | 0% |
| 资产管理 (assets) | ~25 | ~5 | ~20 | 20% |
| 工单管理 (workorders) | ~30 | ~5 | ~25 | 17% |
| 知识库 (knowledge) | ~30 | ~10 | ~20 | 33% |
| 自动化 (automation) | ~25 | ~15 | ~10 | 60% |
| AI助手 (ai) | ~15 | ~6 | ~9 | 40% |
| 认证 (auth) | ~10 | ~0 | ~10 | 0% |
| 通知 (notifications) | ~20 | ~12 | ~8 | 60% |
| 报表 (reports) | ~20 | ~12 | ~8 | 60% |
| 巡检 (inspection) | ~10 | ~0 | ~10 | 0% |
| 部署 (deploy) | ~15 | ~0 | ~15 | 0% |
| 设备发现 (discovery) | ~25 | ~12 | ~13 | 48% |
| 厂商账密 (credentials) | ~15 | ~8 | ~7 | 53% |
| 系统适配 (system) | ~5 | ~4 | ~1 | 80% |
| API密钥 (api-keys) | ~8 | ~0 | ~8 | 0% |
| 其他 | ~15 | ~0 | ~15 | 0% |
| **总计** | **~400** | **~120** | **~280** | **~30%** |

---

*本文档由Hermes Agent自动生成*
