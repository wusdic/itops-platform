# ITOps Platform — Hermes Agent 强制执行规则

> 本文件是 ITOps Platform 的 Agent 行为最高规则。所有任务执行前必须先阅读本文件。
> 文件位置：`HERMES_RULES.md`（项目根目录）
> 最后更新：2026-05-30

---

## 🚨 绝对前提：每次任务必须先读文档入口

**在开始任何任务之前（包括修复 bug、添加功能、代码审查、重构），你必须先执行以下命令：**

```bash
head -50 docs/00-overview/README.md
```

**如果不执行上述命令就擅自开始干活，任务结果将被视为无效。**

---

## 1. 单一事实源（Single Source of Truth）

所有架构、开发、代码取舍决策以 `docs/` 目录下的文档为准：

| 文档 | 作用 |
|---|---|
| `docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md` | 目标架构（最高级依据） |
| `docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md` | 代码取舍与治理方案 |
| `docs/00-overview/README.md` | 文档入口（含 PR 检查清单） |
| `docs/05-implementation/TODO.md` | 当前各 Phase 执行状态 |

**旧文档（`docs/99-archive/`）和根目录的旧 README.md 不再作为开发依据。**

---

## 2. 目录结构说明（消除歧义）

| 目录 | 性质 | 是否当前代码 |
|---|---|---|
| `api/routes/` | 当前后端路由层 | ✅ 是，当前唯一 |
| `modules/business/` | 当前业务逻辑层 | ✅ 是，当前唯一 |
| `modules/collection/` | 当前采集器 | ✅ 是，当前唯一 |
| `backend/app/domains/` | 目标架构（尚未创建） | ❌ 不存在 |
| `docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md` | 目标架构文档 | ✅ 是事实源 |

**当前不存在"旧代码污染新代码"的问题。真正的问题是：docs/ 里的目标架构还未落地为代码。**

---

## 3. 编码禁区

### 3.1 禁止不看 docs/ 就判断"该修什么"
- ❌ 不先读 `docs/00-overview/README.md` 就报告"X 有问题"
- ❌ 不先读 `docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md` 就决定"要修 X"

### 3.2 禁止在未确认问题存在时就修复
- ❌ 在报告"文件 X 不存在"之前，不执行 `find . -name "X" -type d`
- ❌ 修复一个未经 `grep` 或 `git log` 确认的问题

### 3.3 禁止不做验证就提交
- ❌ 不执行 `curl` 或 API 调用验证修复效果，就声称"已修复"
- ❌ 不执行 `python -c "import ..."` 就声称"导入正常"

---

## 4. 任务执行标准流程

### 每个任务必须遵循以下顺序：

```
Step 0: 读入口文档
        → head -50 docs/00-overview/README.md

Step 1: 确认问题存在（用命令验证，不凭记忆）
        → find / grep / curl / git log

Step 2: 读相关 docs/ 章节
        → 找到对应的架构/治理文档段落

Step 3: 制定修复计划（展示给用户）
        → 改哪个文件 + 哪一行 + 预期效果 + 验证方法

Step 4: 执行修复（一次只改一个问题）

Step 5: 验证（curl 或浏览器，不只是看代码）

Step 6: git commit（一个问题一个 commit）

Step 7: 重复 Step 0~6 下一个问题
```

---

## 5. 违规惩罚

如果违背上述规则：
- 任务结果判定为 **0 分**
- 必须立即回退（`git checkout -- .`）
- 重新按 Step 0 执行

---

## 6. 防遗忘触发器

如果对话中出现以下关键词，你的 **Step 0 必须立刻执行**：

- "修复" / "fix" / "优化"
- "为什么"（当涉及代码判断时）
- "验证" / "检查" / "review"
- "Phase X"（任何 Phase）
- 收到新的需求文档（.docx / .md 上传）
- 任何新任务的开始

---

## 7. 项目当前状态（2026-05-30）

| 项目 | 状态 |
|---|---|
| docs/ 事实源 | ✅ 已建立（Phase 0 完成） |
| 目标架构落地（backend/app/domains/） | ❌ 未开始（Phase 1+） |
| Phase 0 遗留问题（N-1~N-14 等） | ⚠️ 待清理 |
| 当前代码与 docs/ 对齐程度 | ❌ 部分对齐，结构性问题未解决 |

**当前优先事项：先清理 Phase 0 遗留问题，不要跳步去做 Phase 1 重构。**
