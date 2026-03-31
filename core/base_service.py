"""
微服务基础类 - 所有服务继承此类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseService(ABC):
    """所有微服务的抽象基类"""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._running = False

    @abstractmethod
    def start(self) -> bool:
        """启动服务"""
        pass

    @abstractmethod
    def stop(self) -> bool:
        """停止服务"""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """健康检查，返回服务状态"""
        pass

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "running": self._running,
        }

    def __repr__(self):
        return f"<Service: {self.name} v{self.version} running={self._running}>"
