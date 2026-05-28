> 文档状态：archived
> 替代文档：
>   - 架构总纲：docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md
>   - 开发计划：docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md
> 归档原因：本文件内容已被新架构文档取代，不再作为开发依据。
> 最后归档日期：2026-05-28

---

# TODO - ITOps Platform（IT运维智能平台）

> ⚠️ **本文档已迁移**：
> - 架构设计 → `DESIGN.md`
> - 实现状态 → `IMPLEMENTATION_STATUS.md`
> - 技术规范 → `SPEC.md`
> - 变更历史 → `CHANGES.md`
>
> 本文档保留作为遗留问题跟踪，不再作为主文档。

## 核心目的
构建智能化、一体化的IT运维管理平台，实现设备自动发现、实时监控告警、工单自动流转、AI辅助决策的完整闭环。

## 项目信息
- 仓库：https://github.com/wusdic/itops_platform
- 当前实现度：~87%（184 项需求中约 160 项已实现）
- 详细状态 → 见 `IMPLEMENTATION_STATUS.md`

## 整体架构
```
前端( Vue 3 + Element Plus ) → API层( FastAPI ) → 业务层( modules/business/ )
                                                      → 采集层( modules/collection/ )
                                                      → 基础层( modules/foundation/ )
                                                      → 存储层( MySQL + Redis + MinIO )
                                                      → AI层( Qwen3.5-0.8B via llama-cpp )
```

---

## 遗留问题（仅 P0/P1）

### P0 级（功能闭环缺口）

| 问题 | 状态 | 说明 |
|------|------|------|
| 增量设备发现 | ⚠️ 部分 | 已有 IP 段扫描，需加定时增量检测 |
| Windows WMI 采集 | ❌ 未实现 | Windows 服务器无法监控 |
| 通知对象精细化 | ⚠️ 部分 | 通知对象已可配置，按类型/级别/设备精准路由未完成 |

### P1 级（完整度提升）

| 问题 | 状态 | 说明 |
|------|------|------|
| 趋势告警（增长率/持续时间） | ❌ 未实现 | CFG-021 |
| SLA 达成率统计 | ❌ 未实现 | WKO-023 |
| 采集模板导入导出 | ❌ 未实现 | CFG-014 |
| 设备配置版本管理 | ❌ 未实现 | CFG-005 |
| 案例 AI 推荐 | ⚠️ 预留 | KNO-014，未集成 |
| 图表数据导出 | ❌ 未实现 | MON-033 |

### P2 级（架构问题）

| 问题 | 说明 |
|------|------|
| P2-1 asset.py / device_api.py 重复 | 95 vs 75 端点，建议合并 |
| P2-2 api/main.py ~490 行 | 建议拆分 |
| P2-3 config/ 6 个 YAML | 建议数据库化管理 |
| P2-4 分片路由 FK 约束 | `_remove_foreign_keys` 需改进 |

---

## 完整实现状态

详细实现状态 → `IMPLEMENTATION_STATUS.md`

完整架构设计 → `DESIGN.md`

技术规范 → `SPEC.md`

---

## 历史记录（保留参考）

> 以下为历史记录，已迁移至 `IMPLEMENTATION_STATUS.md`

### Phase 0-5 完成清单

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 0 | 项目治理 | ✅ |
| Phase 1 | P0 后端缺口 | ✅ |
| Phase 2 | AI 核心 + 高级功能 | ✅ |
| Phase 3 | 前端完善 | ✅ |
| Phase 4 | 测试完善 | ✅ |
| Phase 5 | 交付 | ✅ |

### 新增业务模块
| 模块 | 文件 | 功能 |
|------|------|------|
| root_cause | `modules/business/ai_copilot/root_cause.py` | AI根因分析 |
| remediation | `modules/business/ai_copilot/remediation.py` | AI处置建议引擎 |
| sla_manager | `modules/business/workorder/sla_manager.py` | SLA计时器+升级 |
| rollback | `modules/automation/script_executor/rollback.py` | 执行回滚管理 |
| excel_exporter | `modules/business/report_generator/excel_exporter.py` | Excel导出 |
| inspection_report | `modules/business/report_generator/inspection_report.py` | 巡检报告生成 |
| device_importer | `modules/business/device_importer.py` | 批量设备导入 |
| dashboard_persistence | `modules/business/dashboard/persistence.py` | 仪表盘布局持久化 |

### 新增测试文件
| 测试文件 | 测试数 |
|----------|--------|
| `test_ai_root_cause.py` | 24 |
| `test_ai_remediation.py` | 25 |
| `test_automation_trigger.py` | 23 |
| `test_device_metrics_api.py` | 27 |
| `test_notification.py` | 28 |
| `test_api_keys.py` | ~20 |
| `test_sla_manager.py` | 26 |
| `test_workorder_draft.py` | 15 |
| `test_rollback.py` | 21 |
| `test_workorder_export.py` | 30 |
| `test_inspection_report.py` | 20 |
| `test_dashboard_layout.py` | 34 |
| `test_device_import.py` | 23 |
| **合计** | **~316** |
