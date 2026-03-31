"""
配置加载器
"""
import os
import yaml
from typing import Any, Optional


class ConfigLoader:
    """加载并管理配置文件"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self._config = {}
        self._config_path = config_path
        self._load()

    def _load(self):
        path = self._config_path
        if not os.path.isabs(path):
            # 相对路径转为基于项目根目录的绝对路径
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base, path)
        if not os.path.exists(path):
            print(f"[Config] 配置文件不存在: {path}，使用默认配置")
            return
        with open(path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f) or {}
        print(f"[Config] 配置文件加载成功: {path}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        用点分路径读取配置，如 'weather.city'
        """
        keys = key_path.split(".")
        val = self._config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key_path: str, value: Any) -> None:
        """动态修改配置（不持久化）"""
        keys = key_path.split(".")
        d = self._config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def save(self) -> None:
        """将当前配置持久化到文件"""
        path = self._config_path
        if not os.path.isabs(path):
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base, path)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
        print(f"[Config] 配置已保存: {path}")


# 全局配置实例
config = ConfigLoader()
