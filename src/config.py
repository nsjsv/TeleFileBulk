import configparser
import os
from typing import Dict, Any, Optional, Union


class Config:
    """配置管理类，用于加载和管理应用程序的配置"""

    def __init__(self, config_path: str = "config.ini"):
        """初始化配置管理器
        Args:
            config_path: 配置文件路径
        Raises:
            FileNotFoundError: 当配置文件不存在时抛出
        """
        self._config = configparser.ConfigParser()
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")
        self._config.read(config_path)

    @property
    def telegram(self) -> Dict[str, Union[int, str]]:
        """获取Telegram相关配置
        Returns:
            Dict: 包含api_id和api_hash的配置字典
        """
        return {
            "api_id": self._config.getint("Telegram", "User_ID"),
            "api_hash": self._config.get("Telegram", "User_hash").strip("'"),
            "chat_id": self._config.getint("Telegram", "chat_id"),
        }

    @property
    def proxy(self) -> Optional[Dict[str, Union[str, int]]]:
        """获取代理服务器配置
        Returns:
            Optional[Dict]: 如果启用代理，返回代理配置字典，否则返回None
        """
        # 如果代理未启用，返回None
        if not self._config.getboolean("Proxy", "enable", fallback=False):
            return None

        return {
            "proxy_type": self._config.get("Proxy", "type"),
            "addr": self._config.get("Proxy", "host"),
            "port": self._config.getint("Proxy", "port"),
        }

    @property
    def download(self) -> Dict[str, Any]:
        """获取下载相关配置
        Returns:
            Dict: 包含下载设置的配置字典
        """
        return {
            "separate_reply_folder": self._config.getboolean(
                "Download", "separate_reply_folder", fallback=True
            ),
            "state_file": self._config.get(
                "Download", "state_file", fallback="download_state.json"
            ),
        }

    def get(
        self, section: str, option: str, fallback: Optional[str] = None
    ) -> Optional[str]:
        """获取配置项的值
        Args:
            section: 配置的部分
            option: 配置项名称
            fallback: 当配置项不存在时的默认值
        Returns:
            str: 配置项的值，如果不存在则返回fallback
        """
        return self._config.get(section, option, fallback=fallback)


# 创建全局配置实例
config = Config()
