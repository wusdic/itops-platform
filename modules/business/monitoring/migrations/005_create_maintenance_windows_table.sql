-- Migration: 005_create_maintenance_windows_table.sql
-- 创建维护时段表

CREATE TABLE IF NOT EXISTS `maintenance_windows` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `name` VARCHAR(128) NOT NULL COMMENT '维护时段名称',
    `description` TEXT COMMENT '维护原因/描述',
    `target_type` VARCHAR(32) NOT NULL COMMENT '目标类型: device / rule / tag / ip_range',
    `target_id` VARCHAR(128) COMMENT '目标ID (device_id/rule_id/tag_key)',
    `target_value` VARCHAR(256) COMMENT '目标值 (设备IP/标签值/IP段)',
    `start_time` DATETIME NOT NULL COMMENT '开始时间 (UTC)',
    `end_time` DATETIME NOT NULL COMMENT '结束时间 (UTC)',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `created_by` VARCHAR(64) COMMENT '创建人',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_mw_time_range` (`start_time`, `end_time`),
    INDEX `idx_mw_target` (`target_type`, `target_id`),
    INDEX `idx_mw_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='维护时段表';
