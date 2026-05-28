"""
采集器运行时与状态中心 - Service 层

提供采集器注册、心跳、状态追踪、任务调度的核心业务逻辑
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.common.error_codes import ErrorCode
from app.common.database import get_db_session
from app.domains.collector.schemas import (
    CollectorStatus, CollectorStateInfo, CollectorTaskSubmitRequest,
    TaskStatus, ProtocolType
)


class CollectorRegistry:
    """
    采集器注册表（内存存储，生产环境应使用Redis）
    
    支持功能：
    - 采集器注册/注销
    - 心跳追踪
    - 状态管理
    - 任务队列
    """
    
    _instance = None
    _collectors: Dict[str, Dict[str, Any]] = {}
    _heartbeat_timeout = 60  # 秒，超过此时间未心跳视为离线
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(
        self,
        collector_id: str,
        collector_name: str,
        host: str,
        port: int,
        protocol: str,
        capabilities: List[str],
        version: str = "1.0",
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """注册采集器"""
        now = datetime.now()
        session_token = hashlib.sha256(f"{collector_id}{now.isoformat()}".encode()).hexdigest()[:32]
        
        self._collectors[collector_id] = {
            "collector_id": collector_id,
            "collector_name": collector_name,
            "host": host,
            "port": port,
            "protocol": protocol,
            "capabilities": capabilities,
            "version": version,
            "tags": tags or {},
            "status": CollectorStatus.REGISTERED.value,
            "session_token": session_token,
            "registered_at": now,
            "last_heartbeat": now,
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_in": 0.0,
            "network_out": 0.0,
            "active_tasks": 0,
            "queued_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "error_message": None,
            "error_count": 0,
            "config": {},
            "config_hash": None,
        }
        
        return {
            "collector_id": collector_id,
            "registered_at": now,
            "status": CollectorStatus.REGISTERED.value,
            "session_token": session_token,
            "config": {}
        }
    
    def deregister(self, collector_id: str, reason: Optional[str] = None) -> bool:
        """注销采集器"""
        if collector_id in self._collectors:
            del self._collectors[collector_id]
            return True
        return False
    
    def heartbeat(
        self,
        collector_id: str,
        status: str,
        cpu_usage: Optional[float] = None,
        memory_usage: Optional[float] = None,
        disk_usage: Optional[float] = None,
        network_in: Optional[float] = None,
        network_out: Optional[float] = None,
        active_tasks: int = 0,
        queued_tasks: int = 0,
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """处理采集器心跳"""
        if collector_id not in self._collectors:
            return None
        
        now = datetime.now()
        collector = self._collectors[collector_id]
        
        collector["last_heartbeat"] = now
        collector["status"] = status
        
        if cpu_usage is not None:
            collector["cpu_usage"] = cpu_usage
        if memory_usage is not None:
            collector["memory_usage"] = memory_usage
        if disk_usage is not None:
            collector["disk_usage"] = disk_usage
        if network_in is not None:
            collector["network_in"] = network_in
        if network_out is not None:
            collector["network_out"] = network_out
        if active_tasks is not None:
            collector["active_tasks"] = active_tasks
        if queued_tasks is not None:
            collector["queued_tasks"] = queued_tasks
        
        # 检查是否需要下发命令
        command = None
        config_hash = collector.get("config_hash")
        
        return {
            "acknowledged": True,
            "server_time": now,
            "command": command,
            "config_hash": config_hash
        }
    
    def get_collector(self, collector_id: str) -> Optional[Dict[str, Any]]:
        """获取采集器信息"""
        return self._collectors.get(collector_id)
    
    def get_all_collectors(self) -> List[Dict[str, Any]]:
        """获取所有采集器"""
        self._cleanup_offline()
        return list(self._collectors.values())
    
    def get_collectors_by_protocol(self, protocol: str) -> List[Dict[str, Any]]:
        """根据协议获取采集器"""
        self._cleanup_offline()
        return [
            c for c in self._collectors.values()
            if c["protocol"].lower() == protocol.lower()
            and c["status"] != CollectorStatus.OFFLINE.value
        ]
    
    def get_collectors_by_status(self, status: str) -> List[Dict[str, Any]]:
        """根据状态获取采集器"""
        return [c for c in self._collectors.values() if c["status"] == status]
    
    def update_config(self, collector_id: str, config: Dict[str, Any]) -> Optional[str]:
        """更新采集器配置"""
        if collector_id not in self._collectors:
            return None
        
        config_str = str(config)
        config_hash = hashlib.md5(config_str.encode()).hexdigest()[:16]
        
        self._collectors[collector_id]["config"] = config
        self._collectors[collector_id]["config_hash"] = config_hash
        
        return config_hash
    
    def increment_task_stats(self, collector_id: str, status: str):
        """更新任务统计"""
        if collector_id in self._collectors:
            collector = self._collectors[collector_id]
            if status == TaskStatus.COMPLETED.value:
                collector["completed_tasks"] += 1
            elif status == TaskStatus.FAILED.value:
                collector["failed_tasks"] += 1
            elif status == TaskStatus.RUNNING.value:
                collector["active_tasks"] = max(0, collector["active_tasks"] - 1)
    
    def record_error(self, collector_id: str, error_message: str):
        """记录采集器错误"""
        if collector_id in self._collectors:
            collector = self._collectors[collector_id]
            collector["error_message"] = error_message
            collector["error_count"] += 1
            if collector["error_count"] >= 3:
                collector["status"] = CollectorStatus.ERROR.value
    
    def _cleanup_offline(self):
        """清理离线采集器"""
        now = datetime.now()
        timeout = timedelta(seconds=self._heartbeat_timeout)
        
        for collector_id, collector in list(self._collectors.items()):
            last_heartbeat = collector.get("last_heartbeat")
            if last_heartbeat and (now - last_heartbeat) > timeout:
                if collector["status"] not in [CollectorStatus.OFFLINE.value, CollectorStatus.ERROR.value]:
                    collector["status"] = CollectorStatus.OFFLINE.value
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        self._cleanup_offline()
        
        total = len(self._collectors)
        online = len([c for c in self._collectors.values() 
                     if c["status"] in [CollectorStatus.RUNNING.value, CollectorStatus.IDLE.value]])
        offline = len([c for c in self._collectors.values() 
                      if c["status"] == CollectorStatus.OFFLINE.value])
        error = len([c for c in self._collectors.values() 
                    if c["status"] == CollectorStatus.ERROR.value])
        
        total_tasks = sum(c["active_tasks"] + c["queued_tasks"] + c["completed_tasks"] 
                         for c in self._collectors.values())
        running_tasks = sum(c["active_tasks"] for c in self._collectors.values())
        pending_tasks = sum(c["queued_tasks"] for c in self._collectors.values())
        completed_tasks = sum(c["completed_tasks"] for c in self._collectors.values())
        failed_tasks = sum(c["failed_tasks"] for c in self._collectors.values())
        
        # 协议分布
        protocol_dist: Dict[str, int] = {}
        for c in self._collectors.values():
            p = c["protocol"]
            protocol_dist[p] = protocol_dist.get(p, 0) + 1
        
        return {
            "total_collectors": total,
            "online_collectors": online,
            "offline_collectors": offline,
            "error_collectors": error,
            "total_tasks": total_tasks,
            "running_tasks": running_tasks,
            "pending_tasks": pending_tasks,
            "completed_tasks_today": completed_tasks, "failed_tasks_today": failed_tasks,
            "failed_tasks": failed_tasks,
            "protocol_distribution": protocol_dist
        }


# 全局单例
_collector_registry = CollectorRegistry()


class CollectorService:
    """采集器服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.registry = _collector_registry
    
    def register_collector(self, req) -> Dict[str, Any]:
        """注册采集器"""
        # 检查是否已注册
        existing = self.registry.get_collector(req.collector_id)
        if existing:
            # 已注册，更新信息
            return self.registry.register(
                collector_id=req.collector_id,
                collector_name=req.collector_name,
                host=req.host,
                port=req.port,
                protocol=req.protocol,
                capabilities=req.capabilities,
                version=req.version,
                tags=req.tags
            )
        
        return self.registry.register(
            collector_id=req.collector_id,
            collector_name=req.collector_name,
            host=req.host,
            port=req.port,
            protocol=req.protocol,
            capabilities=req.capabilities,
            version=req.version,
            tags=req.tags
        )
    
    def deregister_collector(self, collector_id: str, reason: Optional[str] = None) -> bool:
        """注销采集器"""
        return self.registry.deregister(collector_id, reason)
    
    def heartbeat(self, req) -> Optional[Dict[str, Any]]:
        """处理心跳"""
        return self.registry.heartbeat(
            collector_id=req.collector_id,
            status=req.status.value if isinstance(req.status, CollectorStatus) else req.status,
            cpu_usage=req.cpu_usage,
            memory_usage=req.memory_usage,
            disk_usage=req.disk_usage,
            network_in=req.network_in,
            network_out=req.network_out,
            active_tasks=req.active_tasks,
            queued_tasks=req.queued_tasks,
            custom_metrics=req.custom_metrics
        )
    
    def get_collector_state(self, collector_id: str) -> Optional[CollectorStateInfo]:
        """获取采集器状态"""
        collector = self.registry.get_collector(collector_id)
        if not collector:
            return None
        
        return CollectorStateInfo(**collector)
    
    def list_collectors(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        protocol: Optional[str] = None,
        collector_id: Optional[str] = None,
        collector_name: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取采集器列表"""
        collectors = self.registry.get_all_collectors()
        
        # 过滤
        if status:
            collectors = [c for c in collectors if c["status"] == status]
        if protocol:
            collectors = [c for c in collectors 
                         if c["protocol"].lower() == protocol.lower()]
        if collector_id:
            collectors = [c for c in collectors 
                        if collector_id.lower() in c["collector_id"].lower()]
        if collector_name:
            collectors = [c for c in collectors 
                        if collector_name.lower() in c["collector_name"].lower()]
        
        total = len(collectors)
        
        # 分页
        offset = (page - 1) * page_size
        collectors = collectors[offset:offset + page_size]
        
        return collectors, total
    
    def get_all_states(self) -> Dict[str, Any]:
        """获取所有采集器状态"""
        collectors = self.registry.get_all_collectors()
        
        total = len(collectors)
        online = len([c for c in collectors 
                    if c["status"] in ["running", "idle"]])
        offline = len([c for c in collectors if c["status"] == "offline"])
        error = len([c for c in collectors if c["status"] == "error"])
        
        return {
            "total": total,
            "online": online,
            "offline": offline,
            "error": error,
            "collectors": [CollectorStateInfo(**c) for c in collectors]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.registry.get_stats()
    
    def update_config(self, collector_id: str, config: Dict[str, Any], config_hash: str) -> Optional[str]:
        """更新采集器配置"""
        return self.registry.update_config(collector_id, config)
    
    def record_task_result(self, task_id: str, collector_id: str, status: str):
        """记录任务结果"""
        self.registry.increment_task_stats(collector_id, status)
        
        # 记录到数据库
        self._save_task_result(task_id, collector_id, status)
    
    def _save_task_result(self, task_id: str, collector_id: str, status: str):
        """保存任务结果到数据库"""
        try:
            # TODO: 保存到数据库
            pass
        except Exception as e:
            pass


class CollectorTaskService:
    """采集任务服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.registry = _collector_registry
    
    def submit_task(self, req: CollectorTaskSubmitRequest) -> Dict[str, Any]:
        """提交采集任务"""
        task_id = req.task_id or str(uuid.uuid4())
        
        # 检查采集器是否存在
        collector = self.registry.get_collector(req.collector_id)
        if not collector:
            return {
                "success": False,
                "error": ErrorCode.COLLECTOR_NOT_FOUND.value
            }
        
        # 检查采集器是否在线
        if collector["status"] == CollectorStatus.OFFLINE.value:
            return {
                "success": False,
                "error": ErrorCode.COLLECTOR_CONNECTION_FAILED.value
            }
        
        # 检查协议支持
        if req.protocol.value not in collector["capabilities"]:
            return {
                "success": False,
                "error": ErrorCode.COLLECTOR_UNSUPPORTED_PROTOCOL.value
            }
        
        now = datetime.now()
        
        # 更新队列任务数
        collector["queued_tasks"] += 1
        
        return {
            "task_id": task_id,
            "submitted_at": now,
            "estimated_duration": req.timeout
        }
    
    def report_result(self, req) -> bool:
        """上报任务结果"""
        self.registry.increment_task_stats(req.collector_id, req.status.value)
        return True
