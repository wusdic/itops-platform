# 自动化模块重构设计方案

> 文档版本：v2.0
> 编制日期：2026-05-23
> 模块：自动化（automation）
> 状态：终稿

---

## 一、核心设计目的（最高优先）

```
事件/告警/工单  →  无直接可用脚本？
                      ↓
              本地大模型自动分析  →  接管处理
                      ↓
              成功解决 → 沉淀为可复用脚本
                      ↓
              后期可单独调用或自由组合
```

**模块定位**：自动化模块是 ITOps 平台的 **AI 驱动执行引擎**，不是简单的脚本仓库。

---

## 二、模块架构

### 2.1 三层架构

```
┌──────────────────────────────────────────────────────┐
│              事件入口层（Event Intake）               │
│  告警触发 | 工单触发 | 手动触发 | 定时触发            │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│           AI 决策引擎（AI Decision Engine）            │
│  LLM 分析 → 有脚本？执行脚本                         │
│          → 无脚本？LLM 生成临时脚本 → 执行            │
│          → 复杂？转工单/人工                         │
│          → 成功后 → 沉淀为正式脚本                    │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│            执行层（Execution Layer）                  │
│  脚本库（Scripts）| 任务调度（Tasks）| 回滚          │
└──────────────────────────────────────────────────────┘
```

### 2.2 关键能力

| 能力 | 说明 |
|------|------|
| **脚本资产化** | 重复操作固化为脚本库，AI 生成脚本标记来源 |
| **任务调度化** | 定时/周期执行，减少人工干预 |
| **执行可追踪** | 每次执行都有记录，可审计、可回滚 |
| **AI 决策** | 无现成脚本时，LLM 自动分析并生成临时脚本 |
| **经验沉淀** | 成功案例 → 推送到知识库 |
| **告警联动** | 触发规则后自动执行脚本（与监控模块闭环） |

---

## 三、与其他模块的边界

### 3.1 自动化模块负责

- 脚本的 CRUD 和执行
- 任务的 CRUD 和调度
- 执行记录的持久化和回滚
- AI 决策逻辑（调用 LLM、决策路由）
- 事件入口的标准化接口

### 3.2 自动化模块不负责（交给其他模块）

| 功能 | 归属模块 | 说明 |
|------|---------|------|
| SOP 生成 | knowledge | 自动化推送案例数据，知识库生成 SOP |
| 脚本推荐 | knowledge | 推荐本质是历史经验，知识库负责 |
| 通知模板 | notification | 自动化决定"何时通知"，通知模块决定"怎么通知" |
| 升级策略 | notification | 值班表、升级规则属于通知模块 |
| 定时调度器 | scheduler（新增） | 统一调度服务，各模块调用 |

### 3.3 模块间接口设计

#### 自动化 → 知识库（推送案例）

```python
# 自动化模块执行成功后调用
POST /api/v1/knowledge/fault-case/from-automation
{
  "source": "automation",
  "automation_execution_id": "exec_xxx",
  "title": "Nginx 服务异常自动恢复",
  "fault_category": "service",
  "fault_level": "P3",
  "symptom": "CPU 使用率超过 90%",
  "root_cause": "Nginx worker 进程僵死",
  "solution": "执行 restart_nginx 脚本",
  "script_id": "script_xxx",
  "execution_params": {"server_ip": "192.168.1.100"},
  "occurrence_time": "2026-05-23T10:00:00Z",
  "resolved_time": "2026-05-23T10:05:00Z",
  "duration_minutes": 5
}
```

#### 自动化 → 知识库（查询推荐脚本）

```python
# AI 决策时调用，查询相似历史案例
GET /api/v1/knowledge/fault-case/recommend-scripts?symptom=CPU使用率异常
# Response
{
  "recommendations": [
    {
      "case_id": "CASE2026050012",
      "title": "Nginx CPU 占用过高自动恢复",
      "matched_script": {
        "script_id": "script_abc123",
        "script_name": "重启 Nginx 服务",
        "success_count": 8
      },
      "similarity": 0.87
    }
  ]
}
```

#### 自动化 → 通知模块（发送升级通知）

```python
# 自动化决定升级时，调用通知模块
POST /api/v1/notification/send
{
  "type": "feishu",
  "title": "自动化处理失败，需要人工介入",
  "content": "事件 xxx 自动处理失败，请及时处理",
  "recipients": ["user_xxx"],
  "escalation": true  # 标记为升级通知
}
```

#### 监控/工单 → 自动化（触发事件）

```python
# 监控模块检测到告警，触发自动化
POST /api/v1/automation/events
{
  "event_type": "alert",
  "event_id": "alert_xxx",
  "source": "monitoring",
  "context": {
    "alert_level": "critical",
    "device_id": 1,
    "device_name": "web-server-01",
    "device_ip": "192.168.1.100",
    "metric_name": "cpu_usage",
    "metric_value": 95.5,
    "threshold": 90.0,
    "triggered_at": "2026-05-23T10:00:00Z"
  }
}
# Response
{
  "event_id": "evt_xxx",
  "ai_decision": {
    "decision": "use_script",  # use_script | generate_script | escalate | human
    "script_id": "script_abc",
    "confidence": 0.92,
    "reason": "历史案例显示该告警 92% 可用 restart_nginx 解决"
  }
}
```

---

## 四、功能清单

### 功能一：事件入口（Event Intake）

| 功能点 | 描述 | 触发源 |
|--------|------|--------|
| 告警触发 | 监控告警触发时自动调起 | `POST /api/v1/automation/events` |
| 工单触发 | 工单创建时 AI 尝试自动处理 | workorder 模块调用 |
| 手动触发 | 用户手动提交事件请求处理 | 前端 |
| 定时触发 | 巡检/例行任务周期执行 | scheduler 模块 |

### 功能二：AI 决策引擎（AI Decision Engine）

| 功能点 | 描述 |
|--------|------|
| 上下文提取 | 从事件中提取告警信息、设备信息、历史记录 |
| LLM 分析 | 调用本地 LLM（ai_copilot）判断处理方式 |
| 脚本生成 | LLM 生成临时脚本并保存（AI 生成标记） |
| 执行决策 | 选择：现有脚本 / 临时脚本 / 转工单 / 人工 |
| 经验沉淀 | 成功案例 → 推送到知识库；AI 生成脚本 → 脚本库 |

**LLM Prompt 模板**：

```
SYSTEM = """你是一个运维自动化助手。
可用脚本列表：
{available_scripts}

当收到事件时，你的决策：
1. 如果有可用脚本 → DECIDE:use_script:<script_id>:<参数>
2. 如果需要生成临时脚本 → DECIDE:generate:<脚本内容>
3. 如果需要人工 → DECIDE:escalate:<原因>

每次决策都要附上置信度（0-1）。"""

USER = """事件类型：{event_type}
事件详情：{event_context}
设备信息：{device_info}
历史工单：{history_workorders}"""
```

### 功能三：脚本库（Scripts）

| 功能点 | 描述 | API |
|--------|------|-----|
| 创建脚本 | 支持 shell/python/ansible，定义参数 schema | `POST /api/v1/automation/scripts` |
| 脚本列表 | 分页、类型过滤、风险等级过滤、关键词搜索 | `GET /api/v1/automation/scripts` |
| 脚本详情 | 查看脚本内容、参数定义、历史执行 | `GET /api/v1/automation/scripts/{id}` |
| 编辑脚本 | 修改内容、参数、标签 | `PUT /api/v1/automation/scripts/{id}` |
| 删除脚本 | 物理删除，被 Task 引用则拒绝 | `DELETE /api/v1/automation/scripts/{id}` |
| 立即执行 | 带参数执行到指定设备，返回 execution_id | `POST /api/v1/automation/scripts/{id}/execute` |
| AI 生成标记 | 脚本来源标记（manual/ai_generated） | 脚本属性 |

### 功能四：任务调度（Tasks）

| 功能点 | 描述 | API |
|--------|------|-----|
| 创建任务 | 绑定脚本 + cron/interval 调度规则 | `POST /api/v1/automation/tasks` |
| 任务列表 | 分页、状态过滤、脚本类型过滤 | `GET /api/v1/automation/tasks` |
| 任务详情 | 查看调度配置、下次/上次执行时间 | `GET /api/v1/automation/tasks/{id}` |
| 编辑任务 | 修改调度规则、启用/禁用 | `PUT /api/v1/automation/tasks/{id}` |
| 删除任务 | 删除调度（不影响执行中的任务） | `DELETE /api/v1/automation/tasks/{id}` |
| 立即执行 | 手动触发，不影响调度周期 | `POST /api/v1/automation/tasks/{id}/run` |

### 功能五：执行记录（Executions）

| 功能点 | 描述 | API |
|--------|------|-----|
| 执行列表 | 分页、状态过滤、任务过滤、时间范围过滤 | `GET /api/v1/automation/executions` |
| 执行详情 | 查看执行参数、目标设备、stdout/stderr | `GET /api/v1/automation/executions/{id}` |
| 执行日志 | 流式输出日志 | `GET /api/v1/automation/executions/{id}/logs` |

### 功能六：告警触发规则（TriggerRules）

| 功能点 | 描述 | API |
|--------|------|-----|
| 创建规则 | 条件 + 动作，条件为指标阈值 | `POST /api/v1/automation/trigger-rules` |
| 规则列表 | 启用/禁用过滤 | `GET /api/v1/automation/trigger-rules` |
| 编辑/删除规则 | | `PUT/DELETE /api/v1/automation/trigger-rules/{id}` |
| 测试规则 | 模拟触发，不记统计 | `POST /api/v1/automation/trigger-rules/{id}/test` |

### 功能七：回滚快照（Rollback）

| 功能点 | 描述 | API |
|--------|------|-----|
| 回滚历史 | 列表展示 | `GET /api/v1/automation/rollback-history` |
| 执行快照 | 查看快照详情 | `GET /api/v1/automation/executions/{id}/snapshot` |
| 执行回滚 | 按快照回滚 | `POST /api/v1/automation/executions/{id}/rollback` |

---

## 五、数据库设计

### 5.1 现有表（监控模块）

| 表名 | 用途 | 归属 |
|------|------|------|
| `automation_scripts` | 脚本库 | automation |
| `automation_tasks` | 任务调度 | automation |
| `automation_executions` | 执行记录 | automation |
| `automation_execution_logs` | 执行日志 | automation |
| `automation_trigger_rules` | 触发规则 | automation |
| `automation_ai_decisions` | AI 决策记录 | automation |
| `automation_script_versions` | 脚本版本 | automation |

### 5.2 新增表（自动化模块）

```sql
-- automation_ai_decisions: AI 执行决策记录（新增）
CREATE TABLE automation_ai_decisions (
    id VARCHAR(36) PRIMARY KEY,
    event_type VARCHAR(32) NOT NULL,  -- alert, workorder, manual
    event_id VARCHAR(36) NOT NULL,
    event_context JSON NOT NULL,
    llm_model VARCHAR(64),
    llm_prompt TEXT,
    llm_response TEXT,
    decision VARCHAR(32) NOT NULL,  -- use_script, generate_script, escalate, human
    script_id VARCHAR(36),
    generated_script_id VARCHAR(36),
    execution_id VARCHAR(36),
    status VARCHAR(32) NOT NULL,  -- pending, success, failed, escalated
    confidence FLOAT,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_decision (decision),
    INDEX idx_status (status)
);

-- automation_script_versions: 脚本版本管理（新增）
CREATE TABLE automation_script_versions (
    id VARCHAR(36) PRIMARY KEY,
    script_id VARCHAR(36) NOT NULL,
    version INT NOT NULL,
    content TEXT NOT NULL,
    change_summary TEXT,
    created_by VARCHAR(64),  -- 'AI' 或用户名
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_script_id (script_id),
    FOREIGN KEY (script_id) REFERENCES automation_scripts(id) ON DELETE CASCADE
);
```

---

## 六、API 完整列表

```
# ============== 事件入口 ==============
POST   /api/v1/automation/events                  # 事件触发（监控/工单/手动）

# ============== Scripts（脚本库）==============
GET    /api/v1/automation/scripts                 # 列表（分页+过滤）
POST   /api/v1/automation/scripts                  # 创建
GET    /api/v1/automation/scripts/{id}            # 详情
PUT    /api/v1/automation/scripts/{id}            # 更新
DELETE /api/v1/automation/scripts/{id}            # 删除
POST   /api/v1/automation/scripts/{id}/execute    # 立即执行
GET    /api/v1/automation/scripts/{id}/versions   # 版本历史
POST   /api/v1/automation/scripts/{id}/promote    # AI脚本转正式（审核后）

# ============== Tasks（任务调度）==============
GET    /api/v1/automation/tasks                  # 列表
POST   /api/v1/automation/tasks                  # 创建
GET    /api/v1/automation/tasks/{id}            # 详情
PUT    /api/v1/automation/tasks/{id}            # 更新
DELETE /api/v1/automation/tasks/{id}            # 删除
POST   /api/v1/automation/tasks/{id}/run        # 立即执行

# ============== Executions（执行记录）==============
GET    /api/v1/automation/executions             # 列表（分页+过滤）
GET    /api/v1/automation/executions/{id}       # 详情
GET    /api/v1/automation/executions/{id}/logs  # 执行日志

# ============== TriggerRules（触发规则）==============
GET    /api/v1/automation/trigger-rules         # 列表
POST   /api/v1/automation/trigger-rules         # 创建
GET    /api/v1/automation/trigger-rules/{id}   # 详情
PUT    /api/v1/automation/trigger-rules/{id}   # 更新
DELETE /api/v1/automation/trigger-rules/{id}   # 删除
POST   /api/v1/automation/trigger-rules/{id}/test  # 测试

# ============== Rollback/Snapshot（回滚）==============
GET    /api/v1/automation/rollback-history
GET    /api/v1/automation/executions/{id}/snapshot
POST   /api/v1/automation/executions/{id}/rollback
```

---

## 七、安全考虑

| 措施 | 说明 |
|------|------|
| 风险等级 | script.risk_level = critical 时执行前二次确认 |
| 参数校验 | 按 params_schema 校验类型、必填 |
| 执行超时 | 默认 5 分钟 |
| 审计日志 | 所有执行写 operation_logs |
| AI 生成脚本 | 标记来源，执行前需审核 |
| 权限控制 | 依赖现有 get_current_user 鉴权 |

---

## 八、验收标准

1. ✅ 事件入口 API 接受告警/工单/手动触发
2. ✅ AI 决策引擎能调用本地 LLM（ai_copilot）并做出决策
3. ✅ 决策为"无脚本"时，LLM 生成临时脚本并存入脚本库（标记 AI 生成）
4. ✅ 脚本库页面（script.vue）能正常 CRUD 脚本
5. ✅ 任务调度页面（task.vue）能创建 cron/interval 任务
6. ✅ 执行历史页面（execute.vue）能看到真实的执行记录
7. ✅ 成功后自动推送案例到知识库
8. ✅ 所有数据持久化到数据库，重启服务不丢失
9. ✅ 原有 trigger-rules API 完全兼容

---

## 九、文件清单

| 操作 | 文件路径 |
|------|---------|
| 新增 | `scripts/migration/011_automation_module.sql` |
| 新增 | `modules/foundation/db_models/automation.py` |
| 新增 | `modules/business/automation/event_handler.py` |
| 新增 | `modules/business/automation/decision_engine.py` |
| 新增 | `modules/business/automation/script_manager.py` |
| 新增 | `modules/business/automation/execution_tracker.py` |
| 修改 | `api/routes/automation.py` |
| 修改 | `frontend/src/views/automation/script.vue` |
| 修改 | `frontend/src/views/automation/task.vue` |
| 修改 | `frontend/src/views/automation/execute.vue` |
| 修改 | `frontend/src/views/automation/ai-panel.vue`（新增） |

---

## 十、依赖关系

```
automation 模块依赖：
├── knowledge 模块（推送案例、查询推荐脚本）
├── notification 模块（发送升级通知）
├── ai_copilot 模块（LLM 调用）
├── scheduler 模块（定时触发）★ 待新增
└── script_executor 模块（实际执行）
```
