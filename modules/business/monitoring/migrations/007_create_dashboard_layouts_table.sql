-- Migration: 007_create_dashboard_layouts_table
-- Desc: 仪表盘自定义布局表 (MON-032)
-- Date: 2026-05-23

CREATE TABLE IF NOT EXISTS dashboard_layouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    layout_id VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(128) DEFAULT '默认布局',
    description VARCHAR(512),
    config TEXT,
    items TEXT,
    column_config TEXT,
    snapshot_data TEXT,
    tags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    INDEX idx_user_layout (user_id, layout_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
