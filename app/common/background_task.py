"""
后台任务封装

提供统一的后台任务创建和管理接口。
基于 asyncio 和线程池。
"""

import asyncio
import logging
from typing import Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

logger = logging.getLogger(__name__)

# 全局线程池
_executor: Optional[ThreadPoolExecutor] = None


def get_executor() -> ThreadPoolExecutor:
    """获取全局线程池"""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="itops-task-")
    return _executor


def run_async(coro):
    """在后台线程中运行异步协程"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def run_in_executor(func: Callable) -> Callable:
    """
    装饰器：将同步函数放到线程池执行

    用法:
        @run_in_executor
        def heavy_compute(data):
            # CPU密集型操作
            return result
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        executor = get_executor()
        future = executor.submit(func, *args, **kwargs)
        return future.result()

    return wrapper


async def run_in_background(coro, task_name: Optional[str] = None) -> asyncio.Task:
    """
    在后台启动一个异步任务

    用法:
        async def my_task():
            await asyncio.sleep(1)
            print("Done")

        task = await run_in_background(my_task())
    """
    task = asyncio.create_task(coro, name=task_name)
    logger.info(f"Background task started: {task_name or 'unnamed'}")
    return task


class BackgroundTask:
    """
    后台任务封装类

    用法:
        task = BackgroundTask(name="sync-device")
        task.run(sync_device, device_id=123)
        task.add_done_callback(on_complete)
    """

    def __init__(self, name: Optional[str] = None):
        self.name = name
        self._future = None

    def run(self, func: Callable, *args, **kwargs) -> None:
        """在线程池中执行任务"""
        executor = get_executor()
        self._future = executor.submit(func, *args, **kwargs)
        if self.name:
            logger.info(f"Background task submitted: {self.name}")

    def add_done_callback(self, callback: Callable) -> None:
        """添加完成回调"""
        if self._future:
            self._future.add_done_callback(callback)

    def result(self, timeout: Optional[float] = None) -> Any:
        """获取任务结果"""
        if self._future:
            return self._future.result(timeout=timeout)

    def done(self) -> bool:
        """检查任务是否完成"""
        if self._future:
            return self._future.done()
        return False
