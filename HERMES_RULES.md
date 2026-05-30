     1|# ITOps Platform — Hermes Agent 强制执行规则
     2|
     3|> 本文件是 ITOps Platform 的 Agent 行为最高规则。所有任务执行前必须先阅读本文件。
     4|> 文件位置：`HERMES_RULES.md`（项目根目录）
     5|> 最后更新：2026-05-30
     6|
     7|---
     8|
     9|## 🚨 绝对前提：每次任务必须先读文档入口
    10|
    11|**在开始任何任务之前（包括修复 bug、添加功能、代码审查、重构），你必须先执行以下命令：**
    12|
    13|```bash
    14|head -50 docs/00-overview/README.md
    15|```
    16|
    17|**如果不执行上述命令就擅自开始干活，任务结果将被视为无效。**
    18|
    19|---
    20|
    21|## 1. 单一事实源（Single Source of Truth）
    22|
    23|所有架构、开发、代码取舍决策以 `docs/` 目录下的文档为准：
    24|
    25|| 文档 | 作用 |
    26||---|---|
    27|| `docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md` | 目标架构（最高级依据） |
    28|| `docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md` | 代码取舍与治理方案 |
    29|| `docs/00-overview/README.md` | 文档入口（含 PR 检查清单） |
    30|| `docs/05-implementation/TODO.md` | 当前各 Phase 执行状态 |
    31|
    32|**旧文档（`docs/99-archive/`）和根目录的旧 README.md 不再作为开发依据。**
    33|
    34|---
    35|
    36|## 2. 目录结构说明（消除歧义）
    37|
    38|| 目录 | 性质 | 是否当前代码 |
    39||---|---|---|
    40|| `api/routes/` | 当前后端路由层 | ✅ 是，当前路由之一（旧） |
    41|| `app/domains/*/router.py` | Phase 1 新路由层 | ✅ 是，当前路由之一（新） |
    42|| `modules/business/` | 当前业务逻辑层 | ✅ 是，当前唯一 |
    43|| `modules/collection/` | 当前采集器 | ✅ 是，当前唯一 |
    44|| `app/common/` | Phase 1 基础设施层 | ✅ 是 |
    45|| `docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md` | 目标架构文档 | ✅ 是事实源 |
    46|
    47|**两个路由层并存（`api/routes/` + `app/domains/*/`）。这是 Phase 1 的实际状态，不是问题。**
    48|
    49|---
    50|
    51|## 3. 编码禁区
    52|
    53|### 3.1 禁止不看 docs/ 就判断"该修什么"
    54|- ❌ 不先读 `docs/00-overview/README.md` 就报告"X 有问题"
    55|- ❌ 不先读 `docs/05-implementation/DETAILED_REFACTOR_AND_GOVERNANCE_PLAN.md` 就决定"要修 X"
    56|
    57|### 3.2 禁止在未确认问题存在时就修复
    58|- ❌ 在报告"文件 X 不存在"之前，不执行 `find . -name "X" -type d`
    59|- ❌ 修复一个未经 `grep` 或 `git log` 确认的问题
    60|
    61|### 3.3 禁止不做验证就提交
    62|- ❌ 不执行 `curl` 或 API 调用验证修复效果，就声称"已修复"
    63|- ❌ 不执行 `python -c "import ..."` 就声称"导入正常"
    64|
    65|---
    66|
    67|## 4. 任务执行标准流程
    68|
    69|### 每个任务必须遵循以下顺序：
    70|
    71|```
    72|Step 0: 读入口文档
    73|        → head -50 docs/00-overview/README.md
    74|
    75|Step 1: 确认问题存在（用命令验证，不凭记忆）
    76|        → find / grep / curl / git log
    77|
    78|Step 2: 读相关 docs/ 章节
    79|        → 找到对应的架构/治理文档段落
    80|
    81|Step 3: 制定修复计划（展示给用户）
    82|        → 改哪个文件 + 哪一行 + 预期效果 + 验证方法
    83|
    84|Step 4: 执行修复（一次只改一个问题）
    85|
    86|Step 5: 验证（curl 或浏览器，不只是看代码）
    87|
    88|Step 6: git commit（一个问题一个 commit）
    89|
    90|Step 7: 重复 Step 0~6 下一个问题
    91|```
    92|
    93|---
    94|
    95|## 5. 违规惩罚
    96|
    97|如果违背上述规则：
    98|- 任务结果判定为 **0 分**
    99|- 必须立即回退（`git checkout -- .`）
   100|- 重新按 Step 0 执行
   101|
   102|---
   103|
   104|## 6. 防遗忘触发器
   105|
   106|如果对话中出现以下关键词，你的 **Step 0 必须立刻执行**：
   107|
   108|- "修复" / "fix" / "优化"
   109|- "为什么"（当涉及代码判断时）
   110|- "验证" / "检查" / "review"
   111|- "Phase X"（任何 Phase）
   112|- 收到新的需求文档（.docx / .md 上传）
   113|- 任何新任务的开始
   114|
   115|---
   116|
   117|## 7. 项目当前状态（2026-05-30）
   118|
   119|| 项目 | 状态 |
   120||---|---|
   121|| docs/ 事实源 | ✅ 已建立（Phase 0 完成） |
   122|| 目标架构落地（backend/app/domains/） | ❌ 未开始（Phase 1+） |
   123|| Phase 0 遗留问题（N-1~N-14 等） | ⚠️ 待清理 |
   124|| 当前代码与 docs/ 对齐程度 | ❌ 部分对齐，结构性问题未解决 |
   125|
   126|**当前优先事项：先清理 Phase 0 遗留问题，不要跳步去做 Phase 1 重构。**
   127|