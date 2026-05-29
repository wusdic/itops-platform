# 变更记录 (2026-05-29)

## 本次修复 (commit fec63e2)

### E2E 链路修复 (共 8 个 bug)

| # | 文件 | 问题 | 修复 |
|---|------|------|------|
| 1 | `modules/collection/device_manager.py` | SNMP/SSH/IPMI 采集成功后缺少 `status=DeviceStatus.ONLINE` | 添加 `status=DeviceStatus.ONLINE` 参数 |
| 2 | `api/routes/monitoring.py` | `device.device_type.value` 在 DB 返回字符串时报 `AttributeError` | 改为安全取值方式 |
| 3 | `modules/business/workorder/workorder.py` | `allowed_fields` 缺少 `'status'` | 补充 `status` 字段 |
| 4 | `api/routes/workorder.py` | `resolve` 调用不存在的 `core.resolve()` → 500 | 改为 `core.update(id, status=RESOLVED, ...)` |
| 5 | `api/routes/workorder.py` | `generate-knowledge` 导入不存在的 `SOPService` | 修正为 `SOPKnowledgeBase` |
| 6 | `modules/business/knowledge_base/sop.py` | `SOPDocument.create()` 传 `metadata=` 但字段名是 `extra_data` | 改为 `extra_data=metadata` |
| 7 | `api/routes/workorder.py` | `generate-knowledge` 返回 `review_status.value` 但字段是字符串 | 改为 `hasattr` 安全取值 |
| 8 | `api/routes/ai.py` | `get_root_cause_analyzer` 未导入导致 `NameError` | 添加 `from modules.business.ai_copilot.root_cause import get_root_cause_analyzer` |

### E2E 验证结果

| 链路 | 状态 | 说明 |
|------|------|------|
| E2E-1 认证 | ✅ | login → token → 受保护接口 → logout |
| E2E-2 资产发现 | ✅ | `POST /scan-and-import-stream` SSE 实时进度 |
| E2E-3 指标采集 | ✅ | SNMP/SSH/IPMI 采集 + status 更新 |
| E2E-4 告警链路 | ✅ | 创建 → 确认 → 关闭 |
| E2E-5 策略链 | ✅ | 冲突检测 / 模拟 / 匹配解释 |
| E2E-6 自动化 | ✅ | 创建脚本 → dry-run → 执行（mock） |
| E2E-7 工单链路 | ✅ | 创建 → 解决 → 生成知识文档 |
| E2E-8 AI分析 | ✅ | 根因分析 / 日志解释 / 历史记录（占位） |

### 遗留说明

- AI `get_analyze_history` 为占位实现（"注：当前版本为占位实现，历史记录暂存于内存"）
- 脚本执行为 mock（`core.py:356` 有 `# TODO: 实际异步执行脚本`）
- `POST /ip/scan` 为 stub（未连接到真实扫描管道），真实入口是 `POST /scan-and-import-stream`
