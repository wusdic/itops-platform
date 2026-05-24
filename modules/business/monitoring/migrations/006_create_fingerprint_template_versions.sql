-- Migration: 006_create_fingerprint_template_versions
-- P0-6: 设备指纹模板版本管理
-- 每次模板变更前保存快照，支持回滚

CREATE TABLE IF NOT EXISTS `fingerprint_template_versions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `version` VARCHAR(64) NOT NULL UNIQUE,
    `description` VARCHAR(255),
    `content` TEXT NOT NULL,
    `operator` VARCHAR(64),
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_fingerprint_template_versions_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
