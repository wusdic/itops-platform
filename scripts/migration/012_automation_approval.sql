-- ============================================================
-- ITOps Platform - 自动化执行审批表
-- 版本: 012
-- 描述: 新增自动化执行审批表 (automation_approval_requests)
-- 运行方式: mysql -u root -p itops_platform < 012_automation_approval.sql
-- ============================================================

USE itops_platform;

-- ============================================================
-- 自动化执行审批请求表
-- ============================================================
CREATE TABLE IF NOT EXISTS automation_approval_requests (
    id VARCHAR(36) PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL COMMENT '关联的执行ID',
    script_id VARCHAR(36) NOT NULL COMMENT '关联的脚本ID',
    risk_level VARCHAR(16) NOT NULL COMMENT '风险等级: low, medium, high, critical',
    required_approval_level INT NOT NULL DEFAULT 0 COMMENT '需要审批等级',
    current_approval_level INT DEFAULT 0 COMMENT '当前审批等级',
    status VARCHAR(32) NOT NULL DEFAULT 'pending' COMMENT '状态: pending, approved, rejected, cancelled, timeout',
    approval_config JSON COMMENT '审批配置: [{level, approvers, mode}]',
    approval_records JSON COMMENT '审批记录: [{level, approver, action, comment, time}]',
    reason TEXT COMMENT '审批原因/说明',
    created_by VARCHAR(64) COMMENT '创建者',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at DATETIME COMMENT '审批过期时间',
    completed_at DATETIME COMMENT '审批完成时间',
    INDEX idx_execution_id (execution_id),
    INDEX idx_status (status),
    INDEX idx_script_id (script_id),
    FOREIGN KEY (execution_id) REFERENCES automation_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (script_id) REFERENCES automation_scripts(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 为 automation_executions 表添加 pending_approval 状态支持
-- (注: 如需修改 ENUM 类型, 使用以下语句)
-- ALTER TABLE automation_executions
-- MODIFY COLUMN status VARCHAR(32) NOT NULL COMMENT 'pending, running, success, failed, cancelled, rolled_back, pending_approval';
-- ============================================================
