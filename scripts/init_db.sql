-- ============================================================
-- ITOps Platform - 数据库初始化脚本
-- 运行方式：mysql -u root -p < init_db.sql
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS itops_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE itops_platform;

-- ============================================================
-- 用户表
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    email VARCHAR(100),
    phone VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login DATETIME,
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入默认管理员账号 (密码: Admin@123456)
-- 密码 hash 是 bcrypt('Admin@123456')
INSERT INTO users (username, password_hash, role, email, status)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyDAoGbVJFLwOa', 'admin', 'admin@itops.local', 'active')
ON DUPLICATE KEY UPDATE username=username;

-- ============================================================
-- 设备表
-- ============================================================
CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    device_type VARCHAR(50),
    vendor VARCHAR(50),
    model VARCHAR(100),
    sn VARCHAR(100),
    os_type VARCHAR(50),
    os_version VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'offline',
    tags TEXT,
    cpu_cores INT DEFAULT 0,
    cpu_usage FLOAT DEFAULT 0,
    memory_total BIGINT DEFAULT 0,
    memory_usage FLOAT DEFAULT 0,
    disk_total BIGINT DEFAULT 0,
    disk_usage FLOAT DEFAULT 0,
    uptime BIGINT DEFAULT 0,
    last_seen DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ip (ip_address),
    INDEX idx_status (status),
    INDEX idx_device_type (device_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 告警表
-- ============================================================
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT,
    alert_name VARCHAR(200) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    message TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    acknowledged_by VARCHAR(50),
    acknowledged_at DATETIME,
    resolved_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_device_id (device_id),
    INDEX idx_severity (severity),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 性能指标表（时序数据，分区表）
-- ============================================================
CREATE TABLE IF NOT EXISTS performance_metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DOUBLE NOT NULL,
    unit VARCHAR(20),
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_device_metric (device_id, metric_name),
    INDEX idx_timestamp (timestamp),
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 工单表
-- ============================================================
CREATE TABLE IF NOT EXISTS work_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    requester VARCHAR(50),
    assignee VARCHAR(50),
    category VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME,
    INDEX idx_status (status),
    INDEX idx_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 备份记录表
-- ============================================================
CREATE TABLE IF NOT EXISTS backup_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT,
    backup_type VARCHAR(20) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    started_at DATETIME,
    completed_at DATETIME,
    error_message TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_device_id (device_id),
    INDEX idx_status (status),
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 网络扫描配置表
-- ============================================================
CREATE TABLE IF NOT EXISTS network_scan_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    ip_range VARCHAR(100) NOT NULL,
    scan_type VARCHAR(20) DEFAULT 'ping',
    port_list VARCHAR(500) DEFAULT '22,80,443,3306,8080',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_scan_at DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 操作日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS operation_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    module VARCHAR(50),
    method VARCHAR(20),
    path VARCHAR(200),
    ip_address VARCHAR(50),
    status_code INT,
    detail TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 系统日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS system_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    module VARCHAR(50),
    message TEXT NOT NULL,
    detail TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level (level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 采集日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS collector_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    collector_name VARCHAR(50) NOT NULL,
    device_id INT,
    device_ip VARCHAR(50),
    status VARCHAR(20) NOT NULL,
    message TEXT,
    duration_ms INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_collector_name (collector_name),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 审计日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 日志配置表
-- ============================================================
CREATE TABLE IF NOT EXISTS log_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT,
    description VARCHAR(200),
    INDEX idx_category (category),
    UNIQUE KEY uk_category_key (category, config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入默认日志配置
INSERT INTO log_configs (category, config_key, config_value, description) VALUES
('operation', 'enabled', 'true', '启用操作日志'),
('operation', 'log_login', 'true', '记录登录事件'),
('operation', 'log_device_crud', 'true', '记录设备增删改查'),
('operation', 'log_alert_action', 'true', '记录告警处理'),
('operation', 'log_workorder_crud', 'true', '记录工单操作'),
('system', 'level', 'WARNING', '系统日志级别'),
('system', 'enabled', 'true', '启用系统日志'),
('collector', 'level', 'ERROR', '采集日志级别'),
('collector', 'enabled', 'true', '启用采集日志'),
('collector', 'log_failed', 'true', '记录采集失败'),
('collector', 'log_offline', 'true', '记录设备离线'),
('collector', 'log_success', 'false', '记录采集成功（不开启）'),
('audit', 'enabled', 'true', '启用审计日志')
ON DUPLICATE KEY UPDATE config_value=config_value;

-- ============================================================
-- 告警统计视图（方便查询）
-- ============================================================
CREATE OR REPLACE VIEW alert_stats AS
SELECT
    severity,
    status,
    COUNT(*) as count
FROM alerts
GROUP BY severity, status;

FLUSH PRIVILEGES;
