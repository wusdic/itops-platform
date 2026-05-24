-- ============================================================
-- ITOps Platform - 自动化模块数据库迁移
-- 版本: 011
-- 描述: 新增自动化模块核心表（脚本库、任务调度、执行记录、AI决策、版本管理）
-- 运行方式: mysql -u root -p itops_platform < 011_automation_module.sql
-- ============================================================

USE itops_platform;

-- ============================================================
-- 1. 自动化脚本库
-- ============================================================
CREATE TABLE IF NOT EXISTS automation_scripts (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    script_type VARCHAR(32) NOT NULL COMMENT 'shell, python, ansible',
    content TEXT NOT NULL,
    risk_level VARCHAR(16) DEFAULT 'medium' COMMENT 'low, medium, high, critical',
    params_schema JSON COMMENT '[{name, type, required, default, description}]',
    tags JSON COMMENT '["nginx", "backup"]',
    source VARCHAR(32) DEFAULT 'manual' COMMENT 'manual, ai_generated',
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_script_type (script_type),
    INDEX idx_risk_level (risk_level),
    INDEX idx_source (source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 2. 自动化任务调度
-- ============================================================
CREATE TABLE IF NOT EXISTS automation_tasks (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    script_id VARCHAR(36) NOT NULL,
    trigger_type VARCHAR(32) NOT NULL COMMENT 'cron, interval, manual',
    trigger_config JSON COMMENT '{"cron": "0 2 * * *"} or {"interval_seconds": 300}',
    target_device_ids JSON COMMENT '[1, 2, 3]，空表示所有',
    enabled BOOLEAN DEFAULT TRUE,
    next_run_time DATETIME,
    last_run_time DATETIME,
    last_execution_id VARCHAR(36),
    status VARCHAR(32) DEFAULT 'idle' COMMENT 'idle, running, error',
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_script_id (script_id),
    INDEX idx_trigger_type (trigger_type),
    INDEX idx_enabled (enabled),
    INDEX idx_status (status),
    FOREIGN KEY (script_id) REFERENCES automation_scripts(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 3. 自动化执行记录
-- ============================================================
CREATE TABLE IF NOT EXISTS automation_executions (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36),
    script_id VARCHAR(36) NOT NULL,
    trigger_type VARCHAR(32) NOT NULL COMMENT 'manual, scheduled, api, alert',
    trigger_params JSON COMMENT '触发时传入的参数',
    status VARCHAR(32) NOT NULL COMMENT 'pending, running, success, failed, cancelled, rolled_back',
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    duration_ms INT COMMENT '毫秒',
    target_devices JSON COMMENT '本次执行的目标设备',
    result_summary JSON COMMENT '{"exit_code": 0, "stdout": "...", "stderr": "..."}',
    error_message TEXT,
    triggered_by VARCHAR(64) COMMENT '用户名或"scheduler"',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_script_id (script_id),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at),
    INDEX idx_trigger_type (trigger_type),
    FOREIGN KEY (script_id) REFERENCES automation_scripts(id) ON DELETE RESTRICT,
    FOREIGN KEY (task_id) REFERENCES automation_tasks(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 4. 自动化执行日志（流式输出）
-- ============================================================
CREATE TABLE IF NOT EXISTS automation_execution_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL,
    stream VARCHAR(16) COMMENT 'stdout, stderr, info',
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_execution_id (execution_id),
    FOREIGN KEY (execution_id) REFERENCES automation_executions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 5. 告警触发规则
-- ============================================================
CREATE TABLE IF NOT EXISTS automation_trigger_rules (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    condition JSON NOT NULL COMMENT '{condition_type, metric_name, operator, threshold_value}',
    alert_level VARCHAR(16) DEFAULT 'medium',
    device_ids JSON,
    device_tags JSON,
    trigger_interval INT DEFAULT 300 COMMENT '秒',
    suppress_enabled BOOLEAN DEFAULT FALSE,
    suppress_duration INT DEFAULT 300 COMMENT '秒',
    suppress_key VARCHAR(128),
    time_windows JSON COMMENT '[{start: "00:00", end: "06:00", days: [1,2,3,4,5]}]',
    actions JSON NOT NULL COMMENT '[{action_type, enabled, script_id, params}]',
    trigger_count INT DEFAULT 0,
    last_triggered_at DATETIME,
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_enabled (enabled),
    INDEX idx_alert_level (alert_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 6. AI 执行决策记录
-- ============================================================
CREATE TABLE IF NOT EXISTS automation_ai_decisions (
    id VARCHAR(36) PRIMARY KEY,
    event_type VARCHAR(32) NOT NULL COMMENT 'alert, workorder, manual',
    event_id VARCHAR(36) NOT NULL,
    event_context JSON NOT NULL COMMENT '原始事件数据',
    llm_model VARCHAR(64) COMMENT '使用的模型',
    llm_prompt TEXT,
    llm_response TEXT,
    decision VARCHAR(32) NOT NULL COMMENT 'use_script, generate_script, escalate, human',
    script_id VARCHAR(36) COMMENT '使用的脚本（如果有）',
    generated_script_id VARCHAR(36) COMMENT 'AI 生成的脚本（如果有）',
    execution_id VARCHAR(36) COMMENT '关联的执行记录',
    confidence FLOAT COMMENT '决策置信度 0-1',
    reason TEXT,
    status VARCHAR(32) NOT NULL COMMENT 'pending, success, failed, escalated',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_event_id (event_id),
    INDEX idx_decision (decision),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 7. 脚本版本管理
-- ============================================================
CREATE TABLE IF NOT EXISTS automation_script_versions (
    id VARCHAR(36) PRIMARY KEY,
    script_id VARCHAR(36) NOT NULL,
    version INT NOT NULL,
    content TEXT NOT NULL,
    change_summary TEXT,
    created_by VARCHAR(64) COMMENT "'AI' 或用户名",
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_script_id (script_id),
    INDEX idx_version (script_id, version),
    FOREIGN KEY (script_id) REFERENCES automation_scripts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
