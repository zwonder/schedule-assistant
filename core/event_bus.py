"""
事件总线 - 服务间通信，实现松耦合
"""
from typing import Callable, Dict, List, Any


class EventBus:
    """简单的发布-订阅事件总线"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers: Dict[str, List[Callable]] = {}
        return cls._instance

    def subscribe(self, event: str, callback: Callable) -> None:
        """订阅一个事件"""
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        """取消订阅"""
        if event in self._subscribers:
            self._subscribers[event].remove(callback)

    def publish(self, event: str, data: Any = None) -> int:
        """发布事件，返回处理该事件的订阅者数量"""
        count = 0
        if event in self._subscribers:
            for callback in self._subscribers[event]:
                try:
                    callback(data)
                    count += 1
                except Exception as e:
                    print(f"[EventBus] 事件处理失败 ({event}): {e}")
        return count


# 全局单例
event_bus = EventBus()
