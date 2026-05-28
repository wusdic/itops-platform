"""
BM-01 监控告警 - 告警服务
提供告警的统一管理接口，包括告警创建、触发、抑制、收敛、升级等

功能：
- 告警创建与状态管理
- 告警触发规则执行
- 告警抑制管理
- 告警收敛协调
- 告警升级处理
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import Session

from modules.foundation.db_models.alert import (
    Alert, AlertLevel, AlertStatus, AlertCategory,
    AlertRule, AlertNotification
)
from modules.business.monitoring.alert_trigger import (
    get_trigger_engine, TriggerRule, TriggerEvent,
    TriggerStatus, TriggerCondition
)
from modules.business.monitoring.alerter import AlertTicket, TicketStatus, get_alert_trigger
from modules.business.monitoring.alert_consolidation import (
    AlertConsolidator, ConsolidationRule, ConsolidatedAlert, ConsolidationStrategy,
    get_alert_consolidator, ConsolidationStrategy
)

logger = logging.getLogger(__name__)


class AlertService:
    """
    告警服务
    提供告警的完整生命周期管理
    """
    
    def __init__(self, db: Session):
        """
        初始化告警服务
        
        Args:
            db: 数据库会话
        """
        self._db = db
        self._trigger = get_alert_trigger()
        self._trigger_engine = get_trigger_engine()
        self._consolidator = get_alert_consolidator()
    
    # ============== 告警基础操作 ==============
    
    def create_alert(
        self,
        title: str,
        level: AlertLevel,
        message: str = "",
        device_id: Optional[int] = None,
        device_name: Optional[str] = None,
        device_ip: Optional[str] = None,
        metric_name: Optional[str] = None,
        metric_value: Optional[float] = None,
        threshold: Optional[float] = None,
        unit: Optional[str] = None,
        category: Optional[AlertCategory] = None,
        tags: Optional[str] = None,
        source: str = "system",
    ) -> Alert:
        """
        创建告警
        
        Args:
            title: 告警标题
            level: 告警级别
            message: 告警消息
            device_id: 设备ID
            device_name: 设备名称
            device_ip: 设备IP
            metric_name: 指标名称
            metric_value: 指标值
            threshold: 阈值
            unit: 单位
            category: 告警分类
            tags: 标签
            source: 告警来源
            
        Returns:
            创建的告警
        """
        # 生成告警唯一键
        import random
        alert_key = f"{device_name or 'system'}-{metric_name or 'unknown'}-{int(datetime.now().timestamp())}-{random.randint(1000, 9999)}"
        
        alert = Alert(
            alert_key=alert_key,
            device_id=device_id,
            device_name=device_name,
            device_ip=device_ip,
            level=level,
            category=category or AlertCategory.OTHER,
            title=title,
            message=message,
            metric_name=metric_name,
            metric_value=str(metric_value) if metric_value is not None else None,
            threshold=str(threshold) if threshold is not None else None,
            unit=unit,
            status=AlertStatus.ACTIVE,
            occurred_at=datetime.now(),
            first_occurred_at=datetime.now(),
            tags=tags,
            source=source,
        )
        
        self._db.add(alert)
        self._db.commit()
        self._db.refresh(alert)
        
        logger.info(f"Created alert: id={alert.id}, key={alert_key}, level={level.value}")
        return alert
    
    def get_alert(self, alert_id: int) -> Optional[Alert]:
        """获取告警"""
        return self._db.query(Alert).filter(Alert.id == alert_id).first()
    
    def get_alert_by_key(self, alert_key: str) -> Optional[Alert]:
        """根据告警键获取告警"""
        return self._db.query(Alert).filter(Alert.alert_key == alert_key).first()
    
    def list_alerts(
        self,
        status: Optional[AlertStatus] = None,
        level: Optional[AlertLevel] = None,
        device_id: Optional[int] = None,
        host: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Alert], int]:
        """
        列出告警
        
        Args:
            status: 状态过滤
            level: 级别过滤
            device_id: 设备ID过滤
            host: 主机名/IP过滤
            page: 页码
            page_size: 每页数量
            
        Returns:
            (告警列表, 总数)
        """
        query = self._db.query(Alert)
        
        if status:
            query = query.filter(Alert.status == status)
        if level:
            query = query.filter(Alert.level == level)
        if device_id:
            query = query.filter(Alert.device_id == device_id)
        if host:
            query = query.filter(
                (Alert.device_name.ilike(f"%{host}%")) |
                (Alert.device_ip.ilike(f"%{host}%"))
            )
        
        total = query.count()
        offset = (page - 1) * page_size
        alerts = query.order_by(Alert.occurred_at.desc()).offset(offset).limit(page_size).all()
        
        return alerts, total
    
    def acknowledge_alert(self, alert_id: int, username: str) -> bool:
        """确认告警"""
        alert = self.get_alert(alert_id)
        if not alert:
            return False
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = username
        alert.acknowledged_at = datetime.now()
        alert.updated_at = datetime.now()
        
        self._db.commit()
        logger.info(f"Alert {alert_id} acknowledged by {username}")
        return True
    
    def resolve_alert(self, alert_id: int, username: str, resolution: str = "") -> bool:
        """解决告警"""
        alert = self.get_alert(alert_id)
        if not alert:
            return False
        
        alert.status = AlertStatus.RESOLVED
        alert.resolved_by = username
        alert.resolved_at = datetime.now()
        alert.resolution_note = resolution
        alert.updated_at = datetime.now()
        
        self._db.commit()
        logger.info(f"Alert {alert_id} resolved by {username}")
        return True
    
    def close_alert(self, alert_id: int, username: str) -> bool:
        """关闭告警"""
        alert = self.get_alert(alert_id)
        if not alert:
            return False
        
        alert.status = AlertStatus.CLOSED
        alert.updated_at = datetime.now()
        
        self._db.commit()
        logger.info(f"Alert {alert_id} closed by {username}")
        return True
    
    def suppress_alert(self, alert_id: int, username: str, reason: str = "") -> bool:
        """抑制告警"""
        alert = self.get_alert(alert_id)
        if not alert:
            return False
        
        alert.status = AlertStatus.SUPPRESSED
        alert.updated_at = datetime.now()
        
        self._db.commit()
        logger.info(f"Alert {alert_id} suppressed by {username}: {reason}")
        return True
    
    def restore_alert(self, alert_id: int, username: str) -> bool:
        """恢复已抑制的告警"""
        alert = self.get_alert(alert_id)
        if not alert or alert.status != AlertStatus.SUPPRESSED:
            return False
        
        alert.status = AlertStatus.ACTIVE
        alert.updated_at = datetime.now()
        
        self._db.commit()
        logger.info(f"Alert {alert_id} restored by {username}")
        return True
    
    def transfer_alert(self, alert_id: int, assignee: str, username: str) -> bool:
        """转派告警"""
        alert = self.get_alert(alert_id)
        if not alert:
            return False
        
        alert.assignee = assignee
        alert.updated_at = datetime.now()
        
        self._db.commit()
        logger.info(f"Alert {alert_id} transferred to {assignee} by {username}")
        return True
    
    # ============== 告警收敛操作 ==============
    
    def consolidate_alert(self, alert_id: int) -> Optional[ConsolidatedAlert]:
        """
        对告警进行收敛处理
        
        Args:
            alert_id: 告警ID
            
        Returns:
            收敛后的告警组
        """
        alert = self.get_alert(alert_id)
        if not alert:
            return None
        
        alert_dict = alert.to_dict()
        return self._consolidator.consolidate_alert(alert_dict)
    
    def get_consolidation_groups(self) -> List[ConsolidatedAlert]:
        """获取所有收敛组"""
        return self._consolidator.get_all_groups()
    
    def get_consolidation_rule(self, rule_id: str) -> Optional[ConsolidationRule]:
        """获取收敛规则"""
        return self._consolidator.get_rule(rule_id)
    
    def list_consolidation_rules(self) -> List[ConsolidationRule]:
        """列出所有收敛规则"""
        return self._consolidator.list_rules()
    
    # ============== 告警触发操作 ==============
    
    def create_trigger_rule(
        self,
        name: str,
        condition_type: str,
        match_conditions: Dict[str, Any],
        alert_level: str = "warning",
        description: str = "",
        enabled: bool = True,
        **kwargs
    ) -> str:
        """
        创建触发规则
        
        Args:
            name: 规则名称
            condition_type: 条件类型
            match_conditions: 匹配条件
            alert_level: 告警级别
            description: 规则描述
            enabled: 是否启用
            **kwargs: 其他参数
            
        Returns:
            规则ID
        """
        import uuid
        
        rule = TriggerRule(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            enabled=enabled,
            condition_type=TriggerCondition(condition_type),
            match_conditions=match_conditions,
            alert_level=alert_level,
            **kwargs
        )
        
        self._trigger_engine.add_rule(rule)
        logger.info(f"Created trigger rule: id={rule.id}, name={name}")
        return rule.id
    
    def evaluate_and_trigger(
        self,
        metric_name: str,
        value: float,
        device_id: int,
        device_name: str,
        device_ip: str,
        previous_value: Optional[float] = None,
        duration_seconds: Optional[int] = None,
    ) -> List[TriggerEvent]:
        """
        评估指标并触发告警
        
        Args:
            metric_name: 指标名称
            value: 当前值
            device_id: 设备ID
            device_name: 设备名称
            device_ip: 设备IP
            previous_value: 前一个值
            duration_seconds: 持续秒数
            
        Returns:
            触发的事件列表
        """
        return self._trigger_engine.evaluate_and_trigger(
            metric_name=metric_name,
            value=value,
            device_id=device_id,
            device_name=device_name,
            device_ip=device_ip,
            previous_value=previous_value,
            duration_seconds=duration_seconds,
        )
    
    # ============== 告警统计 ==============
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取告警统计信息"""
        total = self._db.query(Alert).count()
        active = self._db.query(Alert).filter(
            Alert.status.in_([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED])
        ).count()
        critical = self._db.query(Alert).filter(
            Alert.status == AlertStatus.ACTIVE,
            Alert.level == AlertLevel.CRITICAL
        ).count()
        
        # 按级别统计
        level_counts = {}
        for level in AlertLevel:
            count = self._db.query(Alert).filter(Alert.level == level).count()
            level_counts[level.value] = count
        
        # 按状态统计
        status_counts = {}
        for status in AlertStatus:
            count = self._db.query(Alert).filter(Alert.status == status).count()
            status_counts[status.value] = count
        
        return {
            'total': total,
            'active': active,
            'critical': critical,
            'by_level': level_counts,
            'by_status': status_counts,
        }


# =============================================================================
# 辅助函数
# =============================================================================

def get_alert_service(db: Session) -> AlertService:
    """获取告警服务实例"""
    return AlertService(db)
