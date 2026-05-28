# ITOps Platform 文档体系

> **版本**: v1.0
> **建立日期**: 2026-05-28

---

## 1. 文档体系架构

### 1.1 文档层次

```
README.md                    ← 项目入口（首次访问必读）
    │
    ├── DESIGN.md            ← 架构设计 + 模块详解
    │       └── docs/        ← 详细设计（架构/SRS/测试标准）
    │
    ├── IMPLEMENTATION_STATUS.md  ← 当前实现状态 + 遗留问题
    │
    ├── SPEC.md               ← 技术规范（枚举/字段/API 契约）
    │
    └── CHANGES.md            ← 代码变更历史（追加型）
```

### 1.2 文档职责矩阵

| 文档 | 回答的问题 | 主编写者 | 更新时机 |
|------|-----------|---------|---------|
| README.md | "这是什么？怎么快速跑起来？" | 自动化/手动 | 每次 release |
| DESIGN.md | "系统是怎么设计的？有哪些模块？" | 架构师 | 每次架构变更 |
| IMPLEMENTATION_STATUS.md | "各模块现在实现了多少？缺口在哪？" | 开发者 | 每次迭代 |
| SPEC.md | "代码应该怎么写？枚举值是什么？" | 开发者 | 每次规范决策 |
| CHANGES.md | "这次改了什么？" | 开发者 | 每次 commit |
| docs/*.md | 详细设计/测试/SRS | 架构师/QA | 按需 |

---

## 2. 文档更新规则

### 2.1 强制更新触发条件

**任何代码变更后，必须同步更新以下文档**（如果相关）：

| 变更类型 | 必须更新的文档 |
|---------|--------------|
| 新增 API 端点 | `DESIGN.md`（模块功能表）+ `IMPLEMENTATION_STATUS.md` |
| 新增前端页面 | `DESIGN.md`（页面结构）+ `IMPLEMENTATION_STATUS.md` |
| 新增枚举值/字段 | `SPEC.md`（对应章节） |
| 新增规范决策 | `SPEC.md`（追加新规则） |
| Bug 修复/功能完善 | `CHANGES.md`（追加条目） |

### 2.2 更新流程

```
1. 代码变更完成并通过测试
2. 判断需要更新的文档（按上表）
3. 更新对应文档（追加模式，不删除历史）
4. Git commit message 标注 "docs: ..."
5. 如果是重大变更（新增模块/改变架构），同步更新 README.md
```

### 2.3 Commit Message 规范

```
docs: 更新 DESIGN.md - 新增 X 模块设计
docs: 更新 IMPLEMENTATION_STATUS.md - X 模块实现率更新
docs: 更新 SPEC.md - 新增 Y 字段规范
fix: 修复 Z 问题（同步更新 CHANGES.md）
feat: 新增 X 功能（同步更新 DESIGN.md + IMPLEMENTATION_STATUS.md）
```

---

## 3. 文档质量标准

### 3.1 内容标准

- **README.md**: 5 分钟内让新开发者了解项目并跑起来
- **DESIGN.md**: 让开发者理解架构和模块边界，不读代码也能做技术决策
- **IMPLEMENTATION_STATUS.md**: 精确到每个 API/页面的状态，不可模糊
- **SPEC.md**: 可执行的技术规则，违反则代码 review 必须打回
- **CHANGES.md**: 每条变更独立可读，包含问题描述和解决方案

### 3.2 禁止事项

- ❌ 不删除旧文档内容（只用追加模式）
- ❌ 不创建无法回答具体问题的"万能文档"
- ❌ 不在多个文档中重复相同内容（保持单一事实来源）
- ❌ 不保留"待完成"标记而不标注优先级

---

## 4. 文档生命周期

### 4.1 过期文档处理

以下情况视为"过期文档"，应删除或归档：

| 情况 | 处理方式 |
|------|---------|
| 内容被其他文档完全覆盖 | 删除原文件 |
| 内容已过期且与现状矛盾 | 删除 + 在 CHANGES.md 注明"因过时已删除" |
| 多次迭代产生的 v1/v2/v3 版本 | 删除旧版本，只保留最新 |
| 临时的 debug/验证文档 | 验证完成后删除 |

### 4.2 过期文档清理清单（本次清理）

| 文件 | 处理 |
|------|------|
| `ARCHITECTURE_REPORT.md` | 删除（被 DESIGN.md 替代） |
| `BACKEND_FIX_REPORT.md` | 删除（过时） |
| `GAP_ANALYSIS.md` | 删除（被 IMPLEMENTATION_STATUS.md 替代） |
| `GAP_ANALYSIS_v2.md` | 删除（被 IMPLEMENTATION_STATUS.md 替代） |
| `GAP_ANALYSIS_REPORT.md` | 删除（被 IMPLEMENTATION_STATUS.md 替代） |
| `DEVELOPMENT_PLAN.md` | 删除（过时） |
| `FRONTEND_PLAN.md` | 删除（过时） |
| `PARALLEL_PLAN.md` | 删除（过时） |
| `PLAN_DEVICE_FINGERPRINT.md` | 删除（过时） |
| `VERIFICATION_REPORT.md` | 删除（过时） |
| `DEPLOYMENT_ISSUES.md` | 删除（过时） |
| `CONFIG_GUIDE.md` | 删除（过时） |
| `EXTRACTED_EXPERIENCE.md` | 删除（过时） |
| `verification_log_*.txt` | 删除（临时验证文件） |
| `ARCHITECTURE.md` (docs/) | 删除（被 DESIGN.md 替代） |
| `OVERALL_OPTIMIZATION_AUDIT_2026-05-26.md` | 删除（过时） |
| `OVERALL_OPTIMIZATION_PLAN_2026-05-26.md` | 删除（过时） |
| `REFACTORING_DESIGN.md` | 删除（过时） |
| `FRONTEND_REFACTORING_DESIGN.md` | 删除（过时） |
| `INTEGRATION_ANALYSIS.md` | 删除（过时） |
| `LOGGING_SYSTEM_DESIGN.md` | 删除（过时） |
| `REFACTORING_AUTOMATION.md` | 删除（过时） |
| `TEST_COVERAGE_ANALYSIS.md` | 删除（过时） |
| `TEST_REPORT.md` | 删除（过时） |
| `TESTING_STANDARDS.md` | 删除（已迁移到 docs/TESTING_STANDARDS.md） |
| `TEST_COVERAGE_ANALYSIS.md` | 删除（过时） |
| `API_CONTRACT_GAP_REPORT_2026-05-27.md` | 删除（过时） |
| `API_INVENTORY.md` | 删除（过时） |
| `ITOPS_API_AUDIT.md` | 删除（过时） |
| `API_COVERAGE_REPORT.md` (reports/) | 删除（过时） |
| `API_AUDIT_REPORT.md` (reports/) | 删除（过时） |
| `TASK_PLAN.md` | 删除（过时） |
| `LOG.md` | 删除（过时，已被 CHANGES.md 替代） |
| `整体优化要求.docx` | 删除（过时） |
| `QA_REPORT.md` | 删除（过时） |
| `P2_REFACTOR_DESIGN.md` | 删除（过时） |

**本次清理：36 个文件**

### 4.3 保留文档清单

| 文件 | 保留理由 |
|------|---------|
| `README.md` | 项目入口 |
| `DESIGN.md` | 架构设计主文档 |
| `IMPLEMENTATION_STATUS.md` | 实现状态主文档 |
| `SPEC.md` | 技术规范主文档 |
| `CHANGES.md` | 变更历史主文档 |
| `PHYSICAL_DEPLOY.md` | 物理机部署指南（仍有效） |
| `TODO.md` | 遗留问题跟踪（仍有效） |
| `requirements.txt` | Python 依赖 |
| `frontend/CODING_STANDARDS.md` | 前端编码规范 |
| `docs/ARCH-001-v1.1.0.md` | 架构设计说明书（正式版） |
| `docs/requirements/SRS-001-v1.0.0.md` | 需求规格说明书（正式版） |
| `docs/TESTING_STANDARDS.md` | 测试标准 |
| `docs/DESIGN.md` | 已存在的子目录文档（如有） |

---

## 5. GitHub 文档同步

### 5.1 规则

- 所有文档放在代码仓库根目录或 `docs/` 子目录
- 不使用独立的 Wiki/GitBook/Notion 等外部文档系统
- 不在 README 中链接外部文档（确保离线可访问）

### 5.2 GitHub README 自动同步

项目根目录的 `README.md` 即为 GitHub 仓库首页显示的内容，必须保持简洁。

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-28 | 初始版本，建立文档体系规范 |
