# -*- coding: utf-8 -*-
"""
ITOps Platform - 全局常量定义
集中管理所有魔法数字，提高代码可维护性
"""

# ============== 性能相关 ==============
# 慢请求阈值（毫秒）
SLOW_REQUEST_THRESHOLD_MS = 1000

# 性能指标保留条数
METRICS_RETENTION_LIMIT = 1000

# ============== 导出相关 ==============
# 最大导出条数
MAX_EXPORT_RECORDS = 10000

# ============== 查询限制 ==============
# 查询结果限制
QUERY_RESULT_LIMIT = 1000
QUERY_RESULT_MAX_LIMIT = 10000

# ============== 密码学相关 ==============
# PBKDF2 迭代次数（密码哈希）
PBKDF2_ITERATIONS = 100000

# ============== 时间单位（秒）==============
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400
SECONDS_PER_WEEK = 604800

# ============== 日志相关 ==============
# 日志轮转大小（10MB）
LOG_ROTATION_MAX_BYTES = 10 * 1024 * 1024
# 日志轮转备份数
LOG_ROTATION_BACKUP_COUNT = 5
# 时间轮转间隔
LOG_TIME_ROTATION_INTERVAL = 1
LOG_TIME_ROTATION_WHEN = "midnight"

# ============== 向量数据库 ==============
# Embedding 向量维度
DEFAULT_VECTOR_SIZE = 1536
