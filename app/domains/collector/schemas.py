"""
采集器运行时与状态中心 - Pydantic Schemas

定义采集器注册、心跳、状态追踪的请求/响应模型
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CollectorStatus(str, Enum):
    """采集器状态枚举"""
    REGISTERED = "registered"       # 已注册
    RUNNING = "running"             # 运行中
    IDLE = "idle"                   # 空闲
    ERROR = "error"                 # 错误
    OFFLINE = "offline"             # 离线


class ProtocolType(str, Enum):
    """支持的协议类型"""
    SNMP = "snmp"
    SSH = "ssh"
    WINRM = "winrm"
    IPMI = "ipmi"
    HTTP = "http"
    REDFISH = "redfish"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    BROWSER = "browser"
    MYSQL = "mysql"
    POSTGRES = "postgres"
    REDIS = "redis"
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"
    ELASTICSEARCH = "elasticsearch"
    VMWARE = "vmware"
    ZABBIX = "zabbix"
    PROMETHEUS = "prometheus"


# ========== 采集器注册 ==========

class CollectorRegisterRequest(BaseModel):
    """采集器注册请求"""
    collector_id: str = Field(..., description="采集器唯一标识")
    collector_name: str = Field(..., description="采集器名称")
    host: str = Field(..., description="采集器主机地址")
    port: int = Field(..., description="采集器端口")
    protocol: str = Field(..., description="主协议类型")
    capabilities: List[str] = Field(default_factory=list, description="支持的能力列表")
    version: str = Field(default="1.0", description="采集器版本")
    tags: Optional[Dict[str, str]] = Field(default=None, description="标签")


class CollectorRegisterResponse(BaseModel):
    """采集器注册响应"""
    collector_id: str
    registered_at: datetime
    status: CollectorStatus
    session_token: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ========== 采集器心跳 ==========

class CollectorHeartbeatRequest(BaseModel):
    """采集器心跳请求"""
    collector_id: str = Field(..., description="采集器唯一标识")
    status: CollectorStatus = Field(..., description="当前状态")
    cpu_usage: Optional[float] = Field(default=None, description="CPU使用率(%)")
    memory_usage: Optional[float] = Field(default=None, description="内存使用率(%)")
    disk_usage: Optional[float] = Field(default=None, description="磁盘使用率(%)")
    network_in: Optional[float] = Field(default=None, description="网络入口流量(KB/s)")
    network_out: Optional[float] = Field(default=None, description="网络出口流量(KB/s)")
    active_tasks: int = Field(default=0, description="活跃任务数")
    queued_tasks: int = Field(default=0, description="队列任务数")
    custom_metrics: Optional[Dict[str, Any]] = Field(default=None, description="自定义指标")


class CollectorHeartbeatResponse(BaseModel):
    """采集器心跳响应"""
    acknowledged: bool = True
    server_time: datetime
    command: Optional[str] = None  # stop, restart, reload_config
    config_hash: Optional[str] = None


# ========== 采集器状态 ==========

class CollectorStateInfo(BaseModel):
    """采集器状态信息"""
    collector_id: str
    collector_name: str
    host: str
    port: int
    protocol: str
    status: CollectorStatus
    version: str
    capabilities: List[str]
    tags: Dict[str, str]
    
    # 资源使用
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    
    # 任务统计
    active_tasks: int = 0
    queued_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    
    # 时间戳
    registered_at: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None
    last_task_time: Optional[datetime] = None
    
    # 错误信息
    error_message: Optional[str] = None
    error_count: int = 0

    class Config:
        from_attributes = True


class CollectorStateResponse(BaseModel):
    """采集器状态响应"""
    total: int
    online: int
    offline: int
    error: int
    collectors: List[CollectorStateInfo]


# ========== 采集任务 ==========

class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CollectorTaskSubmitRequest(BaseModel):
    """采集任务提交请求"""
    task_id: str = Field(..., description="任务ID")
    collector_id: str = Field(..., description="指定采集器ID")
    device_id: str = Field(..., description="目标设备ID")
    device_ip: str = Field(..., description="目标设备IP")
    protocol: ProtocolType = Field(..., description="采集协议")
    command: str = Field(..., description="采集命令")
    params: Optional[Dict[str, Any]] = Field(default=None, description="采集参数")
    timeout: int = Field(default=300, description="超时时间(秒)")
    priority: int = Field(default=5, description="优先级 1-10")


class CollectorTaskSubmitResponse(BaseModel):
    """采集任务提交响应"""
    task_id: str
    submitted_at: datetime
    estimated_duration: Optional[int] = None  # 预估耗时(秒)


class CollectorTaskResultRequest(BaseModel):
    """采集任务结果上报"""
    task_id: str = Field(..., description="任务ID")
    collector_id: str = Field(..., description="采集器ID")
    status: TaskStatus = Field(..., description="任务状态")
    start_time: datetime
    end_time: datetime
    data: Optional[Dict[str, Any]] = Field(default=None, description="采集数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    metrics: Optional[Dict[str, Any]] = Field(default=None, description="执行指标")


# ========== 采集器配置 ==========

class CollectorConfigUpdateRequest(BaseModel):
    """采集器配置更新请求"""
    collector_id: str
    config: Dict[str, Any]
    config_hash: str


class CollectorConfigResponse(BaseModel):
    """采集器配置响应"""
    collector_id: str
    config: Dict[str, Any]
    config_hash: str
    updated_at: datetime


# ========== 采集器管理 ==========

class CollectorDeregisterRequest(BaseModel):
    """采集器注销请求"""
    collector_id: str
    reason: Optional[str] = None


class CollectorListRequest(BaseModel):
    """采集器列表查询"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    status: Optional[CollectorStatus] = None
    protocol: Optional[str] = None
    collector_id: Optional[str] = None
    collector_name: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class CollectorStatsResponse(BaseModel):
    """采集器统计信息"""
    total_collectors: int
    online_collectors: int
    offline_collectors: int
    total_tasks: int
    running_tasks: int
    pending_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_response_time_ms: float = 0.0
    protocol_distribution: Dict[str, int]
