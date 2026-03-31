"""
服务注册中心 - 管理所有微服务的注册、发现与调用
"""
from typing import Dict, Optional, List, Any
from core.base_service import BaseService


class ServiceRegistry:
    """服务注册中心（单例）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._services: Dict[str, BaseService] = {}
        return cls._instance

    def register(self, service: BaseService) -> bool:
        """注册一个服务"""
        if service.name in self._services:
            print(f"[Registry] 服务 '{service.name}' 已存在，将被覆盖")
        self._services[service.name] = service
        print(f"[Registry] 服务 '{service.name}' v{service.version} 注册成功")
        return True

    def unregister(self, name: str) -> bool:
        """注销一个服务"""
        if name in self._services:
            del self._services[name]
            print(f"[Registry] 服务 '{name}' 已注销")
            return True
        return False

    def get(self, name: str) -> Optional[BaseService]:
        """获取一个服务实例"""
        return self._services.get(name)

    def list_services(self) -> List[Dict[str, Any]]:
        """列出所有已注册服务"""
        return [svc.get_info() for svc in self._services.values()]

    def start_all(self) -> None:
        """启动所有已注册服务"""
        for name, svc in self._services.items():
            try:
                svc.start()
            except Exception as e:
                print(f"[Registry] 启动服务 '{name}' 失败: {e}")

    def stop_all(self) -> None:
        """停止所有已注册服务"""
        for name, svc in self._services.items():
            try:
                svc.stop()
            except Exception as e:
                print(f"[Registry] 停止服务 '{name}' 失败: {e}")

    def health_report(self) -> Dict[str, Any]:
        """获取所有服务的健康状态"""
        return {name: svc.health_check() for name, svc in self._services.items()}


# 全局单例
registry = ServiceRegistry()
