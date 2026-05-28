# API 路由清单

> 文档状态：current
> 适用版本：v2.0
> 最后更新：2026-05-28
> 维护人：ITOPS 开发团队
> 是否为事实源：yes

---

## 说明

本文档记录所有现有 API 路由，按领域分类。文档归档标识：
- **keep**：功能有价值，可直接纳入新架构
- **adapt**：API 或模型需统一适配后使用
- **refactor**：功能方向正确但实现需重构
- **remove**：过期/重复，应删除

---

## 1. 资产与设备 (adapt)

### asset.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /asset/business | 业务列表 | adapt | 业务系统管理 |
| GET | /asset/business/{business_id} | 业务详情 | adapt | |
| GET | /asset/business/{business_id}/devices | 业务下设备 | adapt | |
| GET | /asset/config | 配置列表 | adapt | |
| POST | /asset/config/snapshot | 配置快照 | adapt | |
| POST | /asset/config/sync/{device_id} | 配置同步 | adapt | |
| GET | /asset/config/{config_id} | 配置详情 | adapt | |
| GET | /asset/device | 设备列表 | adapt | 与 device_api 重复 |
| POST | /asset/device/batch | 批量设备操作 | adapt | |
| GET | /asset/device/{device_id} | 设备详情 | adapt | |
| POST | /asset/device/{device_id}/decommission | 设备退役 | adapt | |
| POST | /asset/device/{device_id}/maintain | 设备维护 | adapt | |
| GET | /asset/group | 分组列表 | adapt | |
| GET | /asset/group/{group_id}/devices | 分组下设备 | adapt | |
| GET | /asset/stats | 资产统计 | adapt | |

### device_api.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /device/adapters/list | 适配器列表 | adapt | |
| GET | /device/adapters/protocols | 协议列表 | adapt | |
| POST | /device/collect | 采集 | adapt | |
| POST | /device/collect/all | 全量采集 | adapt | |
| POST | /device/config/reload | 配置重载 | adapt | |
| GET | /device/config/stats | 配置统计 | adapt | |
| GET | /device/stats | 设备统计 | adapt | |
| GET | /device/{device_id}/metrics/configs | 指标配置 | adapt | |
| GET | /device/{device_name}/metrics | 设备指标 | adapt | |
| GET | /device/{device_name}/metrics/history | 指标历史 | adapt | |
| GET | /device/{device_name}/status | 设备状态 | adapt | |

---

## 2. 设备发现 (keep)

### discovery.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| POST | /discovery/arp/scan | ARP 扫描 | keep | |
| POST | /discovery/devices/import | 导入设备 | keep | |
| GET | /discovery/hosts | 主机列表 | keep | |
| POST | /discovery/import | 导入 | keep | |
| POST | /discovery/ip/hosts | IP 主机 | keep | |
| POST | /discovery/ip/scan | IP 扫描 | keep | |
| POST | /discovery/ip/scan/sync | IP 同步扫描 | keep | |
| GET | /discovery/ip/scan/{task_id}/results | 扫描结果 | keep | |
| GET | /discovery/networks | 网络列表 | keep | |
| POST | /discovery/scan | 扫描 | keep | |
| POST | /discovery/scan-and-import | 扫描并导入 | keep | |
| POST | /discovery/scan-and-import-stream | 流式扫描导入 | keep | |
| GET | /discovery/snmp/devices | SNMP 设备 | keep | |
| POST | /discovery/snmp/discover | SNMP 发现 | keep | |
| POST | /discovery/snmp/scan | SNMP 扫描 | keep | |

---

## 3. 采集与监控 (adapt)

### device_metrics.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /metrics/name/{device_name}/metrics | 设备指标 | adapt | |
| GET | /metrics/{device_id}/metrics | 设备指标 | adapt | |
| POST | /metrics/{device_id}/metrics/bulk | 批量指标 | adapt | |
| GET | /metrics/{device_id}/metrics/categories | 指标分类 | adapt | |

### monitoring.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /monitoring/alerts | 告警列表 | adapt | |
| GET | /monitoring/alerts/statistics | 告警统计 | adapt | |
| GET | /monitoring/alerts/{alert_id} | 告警详情 | adapt | |
| POST | /monitoring/alerts/{alert_id}/acknowledge | 确认告警 | adapt | |
| POST | /monitoring/alerts/{alert_id}/resolve | 解决告警 | adapt | |
| POST | /monitoring/alerts/{alert_id}/restore | 恢复告警 | adapt | |
| POST | /monitoring/alerts/{alert_id}/suppress | 抑制告警 | adapt | |
| POST | /monitoring/alerts/{alert_id}/transfer | 转交告警 | adapt | |
| GET | /monitoring/dashboard/columns | 仪表盘列 | adapt | |
| GET | /monitoring/dashboard/layout | 仪表盘布局 | adapt | |
| GET | /monitoring/dashboards | 仪表盘列表 | adapt | |
| GET | /monitoring/dashboards/{dashboard_id} | 仪表盘详情 | adapt | |

---

## 4. 自动化 (refactor)

### automation.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| POST | /automation/evaluate | 风险评估 | refactor | 缺少状态机 |
| GET | /automation/events | 自动化事件 | refactor | |
| GET | /automation/executions | 执行列表 | refactor | |
| GET | /automation/executions/{execution_id} | 执行详情 | refactor | |
| GET | /automation/executions/{execution_id}/logs | 执行日志 | refactor | 需改进实时性 |
| POST | /automation/executions/{execution_id}/rollback | 回滚执行 | refactor | |
| GET | /automation/executions/{execution_id}/snapshot | 执行快照 | refactor | |
| GET | /automation/scripts | 脚本列表 | refactor | |
| POST | /automation/scripts/{script_id}/execute | 执行脚本 | refactor | |
| GET | /automation/scripts/{script_id}/versions | 脚本版本 | refactor | |
| GET | /automation/tasks | 任务列表 | refactor | |
| POST | /automation/tasks/{task_id}/run | 运行任务 | refactor | |
| GET | /automation/trigger-rules | 触发规则 | refactor | |
| POST | /automation/trigger-rules/{rule_id}/test | 测试规则 | refactor | |

---

## 5. AI / AIOps (adapt)

### ai.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| POST | /ai/analyze | 分析 | adapt | 需结构化输出 |
| GET | /ai/analyze/history | 分析历史 | adapt | |
| GET | /ai/analyze/logs | 分析日志 | adapt | |
| POST | /ai/chat | 聊天 | adapt | 降级为辅助入口 |
| POST | /ai/conversations | 会话 | adapt | |
| GET | /ai/conversations/{conversation_id} | 会话详情 | adapt | |
| GET | /ai/conversations/{conversation_id}/messages | 会话消息 | adapt | |
| POST | /ai/conversations/{conversation_id}/pin | 置顶会话 | adapt | |
| POST | /ai/interpret/report | 解读报告 | adapt | |
| POST | /ai/knowledge-qa | 知识问答 | adapt | |
| POST | /ai/qa | 问答 | adapt | |
| GET | /ai/stats | AI 统计 | adapt | |
| POST | /ai/suggest | 建议 | adapt | |
| POST | /ai/troubleshoot | 故障排查 | adapt | |
| POST | /ai/troubleshoot/auto | 自动排查 | adapt | |

---

## 6. 告警与事件 (adapt)

见 monitoring.py 的告警部分，以及 event 相关（需新建）

---

## 7. 工单 (keep)

### workorder.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /workorder/ | 工单列表 | keep | |
| GET | /workorder/categories | 工单分类 | keep | |
| POST | /workorder/convert-to-workorder | 转为工单 | keep | |
| GET | /workorder/draft/list | 草稿列表 | keep | |
| POST | /workorder/draft/save | 保存草稿 | keep | |
| GET | /workorder/export/{workorder_id} | 导出工单 | keep | |
| GET | /workorder/priorities | 优先级列表 | keep | |
| GET | /workorder/sla/summary | SLA 汇总 | keep | |
| GET | /workorder/stats/summary | 统计汇总 | keep | |
| GET | /workorder/{workorder_id} | 工单详情 | keep | |
| POST | /workorder/{workorder_id}/approve | 审批通过 | keep | |
| POST | /workorder/{workorder_id}/assign | 分配工单 | keep | |

---

## 8. 知识库 (keep)

### knowledge.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /knowledge/category | 分类列表 | keep | |
| GET | /knowledge/fault-case | 故障案例 | keep | |
| GET | /knowledge/fault-case/{case_id} | 案例详情 | keep | |
| GET | /knowledge/graph/nodes | 知识图谱节点 | keep | |
| GET | /knowledge/graph/stats | 图谱统计 | keep | |
| POST | /knowledge/reviews | 提交审核 | keep | |
| POST | /knowledge/reviews/{review_id}/approve | 审核通过 | keep | |

---

## 9. 通知 (adapt)

### notification.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| POST | /notification/alert | 告警通知 | adapt | 变为策略动作 |
| GET | /notification/channels | 通知渠道 | adapt | |
| POST | /notification/send | 发送通知 | adapt | |
| GET | /notification/target-rules | 目标规则 | adapt | |

---

## 10. 系统与配置 (adapt)

### system.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /system/dict | 字典列表 | adapt | |
| GET | /system/logs | 系统日志 | adapt | |
| GET | /system/menu | 菜单 | adapt | |
| GET | /system/settings | 系统设置 | adapt | |
| GET | /system/settings/{key} | 某项设置 | adapt | |

### admin.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /admin/ai/config | AI 配置 | adapt | |
| GET | /admin/api-keys | API Key 列表 | adapt | |
| POST | /admin/backup | 备份 | adapt | |
| GET | /admin/backups | 备份列表 | adapt | |
| GET | /admin/cache/clear | 清除缓存 | adapt | |
| GET | /admin/config | 系统配置 | adapt | |
| GET | /admin/departments | 部门列表 | adapt | |

### config (散落在多处)
| 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|
| /config | 配置项 | adapt | 应统一到配置中心 |
| /api/v1/config/* | API 配置 | adapt | |

---

## 11. 认证与权限 (keep)

### auth.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| POST | /auth/login | 登录 | keep | |
| POST | /auth/logout | 登出 | keep | |
| POST | /auth/ldap-login | LDAP 登录 | keep | |
| GET | /auth/ldap/status | LDAP 状态 | keep | |
| GET | /auth/userinfo | 用户信息 | keep | |
| POST | /auth/refresh | 刷新 Token | keep | |
| GET | /auth/captcha | 验证码 | keep | |

### api_keys.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /api-keys | API Key 列表 | keep | |
| POST | /api-keys | 创建 API Key | keep | |
| POST | /api-keys/{key_id}/activate | 激活 | keep | |
| POST | /api-keys/{key_id}/revoke | 撤销 | keep | |

---

## 12. 凭证管理 (adapt)

### vendor_credentials.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /vendor/probe/banner | 探测 Banner | adapt | |
| GET | /vendor/vendors | 厂商列表 | adapt | |
| GET | /vendor/versions | 版本列表 | adapt | |

---

## 13. 日志服务 (adapt)

### log_service.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /log/get_all | 日志列表 | adapt | 升级为日志中心 |
| GET | /log/stats | 日志统计 | adapt | |

---

## 14. 巡检 (keep)

### inspection.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /inspection/reports/template | 巡检报告模板 | keep | |
| GET | /inspection/reports/{task_id} | 巡检报告 | keep | |
| GET | /inspection/results/{task_id} | 巡检结果 | keep | |
| GET | /inspection/tasks | 巡检任务 | keep | |

---

## 15. 报表 (keep)

### report.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /report/ | 报表列表 | keep | |
| POST | /report/generate | 生成报表 | keep | |
| GET | /report/schedule | 报表计划 | keep | |
| GET | /report/template | 报表模板 | keep | |

---

## 16. 备份恢复 (keep)

### backup.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| POST | /backup/cleanup | 清理备份 | keep | |
| GET | /backup/configs | 备份配置 | keep | |
| POST | /backup/execute | 执行备份 | keep | |
| GET | /backup/history | 备份历史 | keep | |
| POST | /backup/restore/{backup_id} | 恢复备份 | keep | |

---

## 17. 部署管理 (keep)

### deploy.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /api/v1/deploy/health | 部署健康 | keep | |
| GET | /api/v1/deploy/status | 部署状态 | keep | |
| GET | /api/v1/deploy/history | 部署历史 | keep | |
| POST | /api/v1/deploy/canary | 金丝雀部署 | keep | |

---

## 18. 分片路由 (keep)

### sharding.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /sharding/routes/{logical_table} | 分片路由 | keep | |
| POST | /sharding/routes/{logical_table}/create | 创建分片 | keep | |
| GET | /sharding/stats | 分片统计 | keep | |

---

## 19. 水印 (keep)

### watermark.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| POST | /api/v1/watermark/generate | 生成水印 | keep | |
| GET | /api/v1/watermark/list | 水印列表 | keep | |
| POST | /api/v1/watermark/verify | 验证水印 | keep | |

---

## 20. 租户 (adapt)

### tenant.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /tenants/{tenant_id} | 租户详情 | adapt | |
| GET | /tenants/{tenant_id}/quota | 租户配额 | adapt | |
| GET | /tenants/{tenant_id}/users | 租户用户 | adapt | |

---

## 21. 其他适配器 (adapt)

### adapters.py
| 方法 | 路径 | 功能 | 状态 | 说明 |
|------|------|------|------|------|
| GET | /adapters | 适配器列表 | adapt | |
| GET | /adapters/{adapter_id} | 适配器详情 | adapt | |
| GET | /device/{device_id}/protocols | 设备协议 | adapt | |
| POST | /device/{device_id}/protocols/{protocol_type}/test | 测试协议 | adapt | |

---

## 需新建的 API（按目标架构）

| 模块 | API | 说明 |
|------|-----|------|
| event | POST /events | 事件上报 |
| event | GET /events | 事件列表 |
| event | GET /events/{event_id} | 事件详情 |
| state | GET /state/assets/{asset_id} | 资产最新状态 |
| state | GET /state/assets/{asset_id}/history | 状态历史 |
| policy | GET /policies | 策略列表 |
| policy | POST /policies | 创建策略 |
| policy | POST /policies/{policy_id}/simulate | 策略模拟 |
| config | GET /config/definitions | 配置定义 |
| config | POST /config/versions/{id}/release | 发布配置 |
| credential | POST /credentials | 创建凭证 |
| credential | POST /credentials/{id}/test | 测试凭证 |

---

## API 统计

| 状态 | 数量 | 说明 |
|------|------|------|
| keep | ~25 | 保留，直接纳入新架构 |
| adapt | ~60 | 需适配后使用 |
| refactor | ~20 | 需重构 |
| remove | ~5 | 应删除（重复接口） |

---

## 后续工作

1. 对每个 adapt/refactor 的 API 制定适配方案
2. 识别重复 API，确定保留哪个版本
3. 补充缺失的 API（event、state、policy 等）
