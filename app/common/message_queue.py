"""
消息队列抽象

支持多后端：Redis Pub/Sub（默认）、RabbitMQ（可选）。
统一的消息发布/订阅接口。
"""

import logging
from typing import Callable, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class QueueBackend(str, Enum):
    """队列后端类型"""
    REDIS = "redis"
    RABBITMQ = "rabbitmq"


class MessageQueue:
    """
    消息队列抽象

    用法:
        mq = MessageQueue(backend=QueueBackend.REDIS)

        # 发布
        mq.publish("alerts.new", {"alert_id": "123", "severity": "critical"})

        # 订阅
        def handle_alert(data):
            print(f"New alert: {data}")

        mq.subscribe("alerts.new", handle_alert)
    """

    def __init__(self, backend: QueueBackend = QueueBackend.REDIS):
        self.backend = backend
        self._redis = None
        if backend == QueueBackend.REDIS:
            from app.common.redis_client import get_redis_client
            self._redis = get_redis_client()

    def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        """发布消息到频道"""
        import json
        try:
            if self.backend == QueueBackend.REDIS:
                self._redis.publish(channel, json.dumps(message))
                return True
            logger.warning(f"Unsupported queue backend: {self.backend}")
            return False
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            return False

    def subscribe(self, channel: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """订阅频道（阻塞）"""
        if self.backend == QueueBackend.REDIS:
            import json
            pubsub = self._redis.pubsub()
            pubsub.subscribe(channel)
            for msg in pubsub.listen():
                if msg["type"] == "message":
                    try:
                        data = json.loads(msg["data"])
                        handler(data)
                    except Exception as e:
                        logger.error(f"Handler error for {channel}: {e}")
        else:
            logger.warning(f"Unsupported queue backend: {self.backend}")


# 预定义频道
class Channels:
    """消息频道常量"""
    ALERT_NEW = "alerts.new"
    ALERT_RESOLVED = "alerts.resolved"
    AUTOMATION_STARTED = "automation.started"
    AUTOMATION_COMPLETED = "automation.completed"
    AUTOMATION_FAILED = "automation.failed"
    DISCOVERY_PROGRESS = "discovery.progress"
    COLLECTOR_HEARTBEAT = "collector.heartbeat"
    TICKET_CREATED = "ticket.created"
    KNOWLEDGE_APPROVED = "knowledge.approved"


# 全局队列实例
mq = MessageQueue()
