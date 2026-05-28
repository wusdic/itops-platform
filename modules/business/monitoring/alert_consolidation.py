"""
BM-01 监控告警 - 告警收敛模块
提供告警收敛功能，将相似或相关的告警合并为单一告警，减少告警风暴

功能：
- 基于多种维度进行告警收敛（主机、服务、告警类型）
- 支持时间窗口内的告警合并
- 支持收敛规则的优先级配置
- 维护收敛历史记录
"""

import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ConsolidationStrategy(str, Enum):
    """收敛策略枚举"""
    NONE = "none"                    # 不收敛
    DIMENSION = "dimension"          # 按维度收敛（同一设备同类告警）
    TIME_WINDOW = "time_window"      # 时间窗口内收敛
    SERVICE = "service"              # 按服务收敛
    ROOT_CAUSE = "root_cause"       # 按根因收敛（高级，需关联分析）


@dataclass
class ConsolidationRule:
    """
    收敛规则定义
    """
    id: str
    name: str
    description: str = ""
    
    # 启用状态
    enabled: bool = True
    
    # 收敛策略
    strategy: ConsolidationStrategy = ConsolidationStrategy.DIMENSION
    
    # 收敛维度配置
    dimensions: List[str] = field(default_factory=list)
    # 可选维度: device_id, device_ip, device_name, metric_name, alert_type, severity, tags
    
    # 时间窗口配置（秒）
    time_window_seconds: int = 300  # 5分钟内
    
    # 最大收敛数量
    max_consolidated_count: int = 100
    
    # 优先级（数值越小优先级越高）
    priority: int = 100
    
    # 是否创建收敛告警
    create_summary_alert: bool = True
    
    # 摘要模板
    summary_template: str = "检测到 {count} 个相似告警"
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def get_consolidation_key(self, alert: Dict[str, Any]) -> str:
        """
        根据收敛维度生成告警收敛键
        
        Args:
            alert: 告警字典
            
        Returns:
            收敛键字符串
        """
        if self.strategy == ConsolidationStrategy.NONE:
            return f"none_{alert.get('id', 'unknown')}"
        
        if self.strategy == ConsolidationStrategy.TIME_WINDOW:
            # 按时间窗口+维度收敛
            alert_time = alert.get('occurred_at')
            if isinstance(alert_time, str):
                try:
                    alert_time = datetime.fromisoformat(alert_time.replace('Z', '+00:00'))
                except:
                    alert_time = datetime.now()
            
            # 计算时间窗口内的窗口ID
            window_start = alert_time.replace(second=0, microsecond=0)
            minutes = window_start.minute
            window_id = minutes // (self.time_window_seconds // 60)
            window_start = window_start.replace(minute=(window_id * (self.time_window_seconds // 60)))
            
            dim_values = []
            for dim in self.dimensions:
                val = alert.get(dim, 'unknown')
                dim_values.append(f"{dim}={val}")
            
            return f"{window_start.isoformat()}_{'_'.join(dim_values)}"
        
        # 默认按维度收敛
        dim_values = []
        for dim in self.dimensions:
            val = alert.get(dim, 'unknown')
            dim_values.append(f"{dim}={val}")
        
        return "_".join(dim_values)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'enabled': self.enabled,
            'strategy': self.strategy.value if isinstance(self.strategy, ConsolidationStrategy) else self.strategy,
            'dimensions': self.dimensions,
            'time_window_seconds': self.time_window_seconds,
            'max_consolidated_count': self.max_consolidated_count,
            'priority': self.priority,
            'create_summary_alert': self.create_summary_alert,
            'summary_template': self.summary_template,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
        }


@dataclass
class ConsolidatedAlert:
    """
    收敛后的告警组
    """
    consolidation_key: str
    strategy: ConsolidationStrategy
    
    # 成员告警
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    
    # 收敛信息
    first_occurred_at: Optional[datetime] = None
    last_occurred_at: Optional[datetime] = None
    count: int = 0
    
    # 最高级别告警信息
    highest_level: str = "info"
    highest_level_count: int = 0
    
    # 摘要信息
    summary: str = ""
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_alert(self, alert: Dict[str, Any]):
        """添加告警到收敛组"""
        self.alerts.append(alert)
        self.count = len(self.alerts)
        
        alert_time = alert.get('occurred_at')
        if isinstance(alert_time, str):
            try:
                alert_time = datetime.fromisoformat(alert_time.replace('Z', '+00:00'))
            except:
                alert_time = datetime.now()
        
        if self.first_occurred_at is None or alert_time < self.first_occurred_at:
            self.first_occurred_at = alert_time
        if self.last_occurred_at is None or alert_time > self.last_occurred_at:
            self.last_occurred_at = alert_time
        
        # 更新最高级别
        level_priority = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        alert_level = alert.get('level', 'info')
        current_priority = level_priority.get(self.highest_level, 4)
        new_priority = level_priority.get(alert_level, 4)
        if new_priority < current_priority:
            self.highest_level = alert_level
        
        # 统计最高级别告警数量
        if alert_level == self.highest_level:
            self.highest_level_count += 1
        
        self.updated_at = datetime.now()
    
    def get_duration_seconds(self) -> int:
        """获取持续时间（秒）"""
        if self.first_occurred_at and self.last_occurred_at:
            return int((self.last_occurred_at - self.first_occurred_at).total_seconds())
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'consolidation_key': self.consolidation_key,
            'strategy': self.strategy.value if isinstance(self.strategy, ConsolidationStrategy) else self.strategy,
            'count': self.count,
            'first_occurred_at': self.first_occurred_at.isoformat() if self.first_occurred_at else None,
            'last_occurred_at': self.last_occurred_at.isoformat() if self.last_occurred_at else None,
            'duration_seconds': self.get_duration_seconds(),
            'highest_level': self.highest_level,
            'highest_level_count': self.highest_level_count,
            'summary': self.summary,
            'alerts': self.alerts,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class AlertConsolidator:
    """
    告警收敛器
    负责管理收敛规则和执行告警收敛操作
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化告警收敛器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self._rules: Dict[str, ConsolidationRule] = {}
        self._consolidated_groups: Dict[str, ConsolidatedAlert] = {}
        
        # 注册默认收敛规则
        self._setup_default_rules()
        
        logger.info('AlertConsolidator initialized')
    
    def _setup_default_rules(self):
        """设置默认收敛规则"""
        # 默认按设备+指标名称收敛
        default_rule = ConsolidationRule(
            id="default_device_metric",
            name="设备指标收敛",
            description="同一设备同类指标的告警进行收敛",
            strategy=ConsolidationStrategy.DIMENSION,
            dimensions=["device_id", "metric_name"],
            time_window_seconds=300,
            max_consolidated_count=50,
            priority=100,
        )
        self._rules[default_rule.id] = default_rule
        
        # 按服务收敛（需要标签支持）
        service_rule = ConsolidationRule(
            id="service_consolidation",
            name="服务收敛",
            description="同一服务内的告警进行收敛",
            strategy=ConsolidationStrategy.DIMENSION,
            dimensions=["tags", "alert_type"],
            time_window_seconds=600,
            max_consolidated_count=100,
            priority=90,
        )
        self._rules[service_rule.id] = service_rule
    
    def add_rule(self, rule: ConsolidationRule) -> str:
        """
        添加收敛规则
        
        Args:
            rule: 收敛规则
            
        Returns:
            规则ID
        """
        self._rules[rule.id] = rule
        logger.info(f'Added consolidation rule: {rule.id} - {rule.name}')
        return rule.id
    
    def update_rule(self, rule: ConsolidationRule):
        """更新收敛规则"""
        rule.updated_at = datetime.now()
        self._rules[rule.id] = rule
    
    def delete_rule(self, rule_id: str) -> bool:
        """删除收敛规则"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[ConsolidationRule]:
        """获取收敛规则"""
        return self._rules.get(rule_id)
    
    def list_rules(self, enabled_only: bool = False) -> List[ConsolidationRule]:
        """
        列出收敛规则
        
        Args:
            enabled_only: 只返回启用的规则
            
        Returns:
            收敛规则列表
        """
        rules = list(self._rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return sorted(rules, key=lambda r: r.priority)
    
    def consolidate_alert(
        self,
        alert: Dict[str, Any],
        rule_id: Optional[str] = None
    ) -> ConsolidatedAlert:
        """
        将告警进行收敛处理
        
        Args:
            alert: 告警字典
            rule_id: 收敛规则ID（不指定则自动选择最佳规则）
            
        Returns:
            收敛后的告警组
        """
        # 选择收敛规则
        if rule_id:
            rule = self._rules.get(rule_id)
            if not rule or not rule.enabled:
                return None
        else:
            # 自动选择最高优先级规则
            rules = self.list_rules(enabled_only=True)
            if not rules:
                return None
            rule = rules[0]
        
        # 生成收敛键
        consolidation_key = rule.get_consolidation_key(alert)
        
        # 检查是否已存在收敛组
        if consolidation_key in self._consolidated_groups:
            group = self._consolidated_groups[consolidation_key]
            
            # 检查是否超过最大数量
            if group.count >= rule.max_consolidated_count:
                logger.warning(f"Consolidation group {consolidation_key} reached max count")
                return group
            
            group.add_alert(alert)
        else:
            # 创建新的收敛组
            group = ConsolidatedAlert(
                consolidation_key=consolidation_key,
                strategy=rule.strategy,
            )
            group.add_alert(alert)
            group.summary = rule.summary_template.format(
                count=group.count,
                device_name=alert.get('device_name', 'unknown'),
                metric_name=alert.get('metric_name', 'unknown'),
            )
            self._consolidated_groups[consolidation_key] = group
        
        return group
    
    def get_consolidated_group(self, consolidation_key: str) -> Optional[ConsolidatedAlert]:
        """获取收敛组"""
        return self._consolidated_groups.get(consolidation_key)
    
    def get_all_groups(self) -> List[ConsolidatedAlert]:
        """获取所有收敛组"""
        return list(self._consolidated_groups.values())
    
    def clear_old_groups(self, hours: int = 24):
        """
        清理旧的收敛组
        
        Args:
            hours: 清理多少小时前的收敛组
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        to_remove = []
        
        for key, group in self._consolidated_groups.items():
            if group.updated_at < cutoff:
                to_remove.append(key)
        
        for key in to_remove:
            del self._consolidated_groups[key]
        
        logger.info(f"Cleared {len(to_remove)} old consolidation groups")
        return len(to_remove)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取收敛统计信息"""
        groups = list(self._consolidated_groups.values())
        
        total_alerts = sum(g.count for g in groups)
        level_distribution = {}
        
        for group in groups:
            for alert in group.alerts:
                level = alert.get('level', 'unknown')
                level_distribution[level] = level_distribution.get(level, 0) + 1
        
        return {
            'total_groups': len(groups),
            'total_consolidated_alerts': total_alerts,
            'reduction_ratio': f"{(1 - len(groups) / total_alerts * 100):.1f}%" if total_alerts > 0 else "0%",
            'level_distribution': level_distribution,
            'active_rules': len(self.list_rules(enabled_only=True)),
        }


# =============================================================================
# 全局 AlertConsolidator 单例
# =============================================================================
_consolidator: Optional[AlertConsolidator] = None


def get_alert_consolidator() -> AlertConsolidator:
    """获取全局 AlertConsolidator 单例"""
    global _consolidator
    if _consolidator is None:
        _consolidator = AlertConsolidator()
    return _consolidator
