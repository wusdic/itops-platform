"""
Redis 工具

提供统一的 Redis 操作接口：缓存、锁、发布订阅。
"""

import json
import logging
from typing import Optional, Any
from contextlib import contextmanager

import redis

from api.dependencies import get_settings

logger = logging.getLogger(__name__)

# Global redis client
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """获取 Redis 客户端（单例）"""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
    return _redis_client


class RedisCache:
    """Redis 缓存封装"""

    def __init__(self, client: Optional[redis.Redis] = None):
        self.client = client or get_redis_client()

    def get(self, key: str) -> Optional[str]:
        """获取值"""
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None

    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """设置值"""
        try:
            self.client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False

    def get_json(self, key: str) -> Optional[Any]:
        """获取 JSON 值"""
        val = self.get(key)
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                return None
        return None

    def set_json(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置 JSON 值"""
        try:
            return self.set(key, json.dumps(value), expire)
        except Exception as e:
            logger.error(f"Redis SET JSON error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """删除键"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False


class RedisLock:
    """Redis 分布式锁"""

    def __init__(self, client: Optional[redis.Redis] = None):
        self.client = client or get_redis_client()

    @contextmanager
    def acquire(
        self,
        key: str,
        expire: int = 30,
        wait_timeout: int = 10,
    ):
        """
        获取分布式锁

        用法:
            lock = RedisLock()
            with lock.acquire("my-lock"):
                # 临界区
                pass
        """
        lock_key = f"lock:{key}"
        import time
        start = time.time()
        while True:
            acquired = self.client.set(lock_key, "1", nx=True, ex=expire)
            if acquired:
                try:
                    yield
                finally:
                    self.client.delete(lock_key)
                return
            if time.time() - start >= wait_timeout:
                raise TimeoutError(f"Failed to acquire lock: {key}")
            time.sleep(0.1)

    def release(self, key: str) -> bool:
        """手动释放锁"""
        try:
            self.client.delete(f"lock:{key}")
            return True
        except Exception:
            return False


# 全局缓存实例
cache = RedisCache()
