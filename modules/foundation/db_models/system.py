"""
操作日志数据库模型
用于记录系统操作日志
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func

from .base import Base


class OperationLog(Base):
    """
    操作日志模型
    记录用户在系统中的操作行为
    """
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 操作信息
    username = Column(String(64), index=True, nullable=False)
    action = Column(String(64), index=True)  # create, update, delete, login, etc.
    resource = Column(String(64), index=True)  # device, workorder, alert, etc.
    resource_id = Column(String(64))  # 操作资源的ID

    # 操作详情
    method = Column(String(16))  # GET, POST, PUT, DELETE
    path = Column(String(256))
    ip_address = Column(String(64))
    user_agent = Column(String(256))

    # 请求和响应
    request_body = Column(Text)  # 请求参数（脱敏）
    response_status = Column(Integer)  # 响应状态码
    error_message = Column(Text)

    # 执行信息
    duration_ms = Column(Integer)  # 执行时长（毫秒）

    # 时间戳
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 索引
    __table_args__ = (
        Index('idx_user_action_time', 'username', 'action', 'timestamp'),
        Index('idx_resource_time', 'resource', 'resource_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<OperationLog(user={self.username}, action={self.action}, resource={self.resource})>"


class BackupRecord(Base):
    """
    备份记录模型
    记录数据库备份信息
    """
    __tablename__ = "backup_records"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 备份信息
    backup_type = Column(String(32))  # full, incremental, config
    file_name = Column(String(256))
    file_path = Column(String(512))
    file_size = Column(Integer)  # bytes

    # 备份状态
    status = Column(String(32))  # pending, running, completed, failed
    error_message = Column(Text)

    # 备份位置
    storage_type = Column(String(32))  # local, remote
    storage_path = Column(String(512))

    # 操作信息
    created_by = Column(String(64))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<BackupRecord(id={self.id}, type={self.backup_type}, status={self.status})>"


class APIKey(Base):
    """
    API Key模型
    用于API接口认证
    """
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Key信息
    key_id = Column(String(64), unique=True, index=True, nullable=False)  # key标识符
    key_hash = Column(String(256), nullable=False)  # key的hash值
    key_prefix = Column(String(16), nullable=False)  # key的前缀（用于显示）

    # 使用者信息
    name = Column(String(128), nullable=False)  # key名称/描述
    user_id = Column(String(64), index=True)  # 关联用户ID
    username = Column(String(64))  # 用户名

    # 权限范围
    scopes = Column(Text)  # JSON数组，可访问的scope列表

    # 状态
    is_active = Column(Integer, default=1)  # 1=激活, 0=禁用
    is_revoked = Column(Integer, default=0)  # 1=已撤销, 0=正常

    # 有效期
    expires_at = Column(DateTime)  # 过期时间，为空表示永不过期

    # 使用限制
    max_requests = Column(Integer)  # 最大请求数，-1表示无限制
    request_count = Column(Integer, default=0)  # 当前请求计数

    # 速率限制
    rate_limit = Column(Integer, default=100)  # 每分钟请求数限制
    rate_limit_window = Column(Integer, default=60)  # 速率限制时间窗口(秒)

    # 使用记录
    last_used_at = Column(DateTime)  # 最后使用时间
    last_used_ip = Column(String(64))  # 最后使用的IP

    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(64))  # 创建者

    # 索引
    __table_args__ = (
        Index('idx_api_key_active', 'is_active', 'is_revoked'),
        Index('idx_api_key_user', 'user_id', 'is_active'),
    )

    def __repr__(self):
        return f"<APIKey(id={self.id}, key_id='{self.key_id}', name='{self.name}')>"

    def is_valid(self) -> bool:
        """检查key是否有效"""
        if self.is_revoked or not self.is_active:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        if self.max_requests > 0 and self.request_count >= self.max_requests:
            return False
        return True


class LogConfig(Base):
    """
    日志配置模型
    控制各类型日志的记录开关和级别
    """
    __tablename__ = "log_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(32), nullable=False, index=True)  # operation/system/collection/audit
    sub_category = Column(String(64), nullable=False)  # login/device_crud/error/success/...
    enabled = Column(Integer, default=1)  # 1=记录, 0=不记录
    min_level = Column(String(16), default="INFO")  # DEBUG/INFO/WARNING/ERROR/CRITICAL
    aggregation_enabled = Column(Integer, default=1)  # 是否归集
    retention_days = Column(Integer, default=7)  # 保留天数
    description = Column(String(256))  # 中文说明
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_category_sub', 'category', 'sub_category', unique=True),
    )


class LogGroup(Base):
    """
    日志归集组
    同一归集键的多条日志聚合为一个组
    """
    __tablename__ = "log_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(32), nullable=False, index=True)
    group_key = Column(String(256), nullable=False)  # 归集唯一标识
    dimension_summary = Column(Text)  # JSON: {action: 'login', count: 42, ...}
    first_seen = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    total_count = Column(Integer, default=0)
    level_distribution = Column(Text)  # JSON: {ERROR: 3, WARNING: 10}
    sample_log = Column(Text)  # 代表性日志原文
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_cat_key', 'category', 'group_key'),
        Index('idx_last_seen', 'last_seen'),
    )


class LogItem(Base):
    """
    日志明细
    归集组内的单条日志
    """
    __tablename__ = "log_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, index=True)
    category = Column(String(32), nullable=False, index=True)
    raw_content = Column(Text)  # 原始日志全文
    level = Column(String(16), index=True)  # DEBUG/INFO/WARNING/ERROR
    source = Column(String(64))
    message = Column(Text)
    detail = Column(Text)  # JSON 结构化详情
    duration_ms = Column(Integer)
    username = Column(String(64), index=True)
    ip_address = Column(String(64))
    resource_type = Column(String(64), index=True)
    resource_id = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index('idx_cat_created', 'category', 'created_at'),
    )


class SystemUser(Base):
    """
    系统用户模型
    存储系统用户信息（从 InMemoryUserStore 迁移而来）
    """
    __tablename__ = "system_users"

    id = Column(String(64), primary_key=True)  # 用户ID，如 u001
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    email = Column(String(128))
    status = Column(String(32), default="active")  # active/inactive/locked/pending
    roles = Column(Text)  # JSON 数组存储角色列表
    last_login = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_username_active', 'username', 'status'),
    )


class NetworkScanConfig(Base):
    """
    网段扫描配置
    存储用户配置的扫描网段，替代内存存储
    """
    __tablename__ = "network_scan_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    ip_range = Column(String(100), nullable=False)  # CIDR 格式
    scan_type = Column(String(20), default="ping")
    port_list = Column(String(500), default="22,80,443,3306,8080")
    status = Column(String(20), default="active")  # active/inactive
    auto_scan = Column(Integer, default=0)  # 0=手动, 1=自动
    last_scan_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_status', 'status'),
    )


class DiscoveryTask(Base):
    """
    设备发现任务
    存储用户创建的扫描任务
    """
    __tablename__ = "discovery_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), unique=True, nullable=False, index=True)  # task-YYYYMMDDHHMMSS
    name = Column(String(200), nullable=False)
    task_type = Column(String(32), nullable=False)  # ip_scan / snmp_discovery
    target = Column(String(256), nullable=False)  # CIDR 或 IP 列表
    options = Column(Text)  # JSON 配置
    schedule = Column(String(64))  # Cron 表达式
    status = Column(String(32), default="created")  # created/running/completed/failed
    created_by = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_task_type', 'task_type'),
        Index('idx_status', 'status'),
    )
