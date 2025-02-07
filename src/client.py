from telethon import TelegramClient
from typing import Dict, Any, Optional
from src.config import Config

# 加载配置
config = Config()

# 获取配置信息
telegram_config: Dict[str, Any] = config.telegram
proxy_config: Optional[Dict[str, Any]] = config.proxy
download_config: Dict[str, Any] = config.download

# 创建Telegram客户端
client_kwargs = {
    'session': 'anon',
    'api_id': telegram_config['api_id'],
    'api_hash': telegram_config['api_hash']
}

# 如果启用了代理，添加代理配置
if proxy_config:
    print(f"使用{proxy_config['proxy_type']}代理: {proxy_config['addr']}:{proxy_config['port']}")
    client_kwargs['proxy'] = proxy_config
else:
    print("不使用代理")

# 创建Telegram客户端
client = TelegramClient(**client_kwargs)

# 目标群组ID
CHAT_ID: int = -1002181058156

# 导出必要的配置和客户端
__all__ = ['client', 'CHAT_ID', 'config', 'download_config']
