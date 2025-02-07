import re
import os
from typing import Any, Optional
from telethon.tl.custom import Message

def sanitize_filename(name: str, use_underscore: bool = False) -> str:
    """清理文件名，移除非法字符
    Args:
        name: 原始文件名
        use_underscore: 是否使用下划线替换非法字符
    Returns:
        str: 清理后的文件名
    """
    replacement = '_' if use_underscore else ''
    return re.sub(r'[<>:"/\\|?*]', replacement, name)

def get_file_name(msg: Message, index: Optional[int] = None) -> str:
    """获取文件名
    Args:
        msg: 消息对象
        index: 可选的自动编号
    Returns:
        str: 文件名
    """
    # 如果是文档类型，尝试获取原始文件名
    if msg.document and hasattr(msg.document, 'attributes'):
        for attr in msg.document.attributes:
            if hasattr(attr, 'file_name') and attr.file_name:
                return attr.file_name
    
    # 如果是照片，使用p{index}.jpg的格式
    if msg.photo:
        return f'p{index if index else 1}.jpg'
    
    # 其他类型的文件，使用file{index}格式
    return f'file{index if index else 1}'

async def get_folder_name(msg: Message, client: Any, chat_id: int) -> str:
    """获取文件夹名称
    Args:
        msg: 消息对象
        client: Telegram客户端
        chat_id: 聊天ID
    Returns:
        str: 文件夹名称
    """
    msg_id = msg.id
    
    # 如果是群组消息，获取同组中有文本的消息
    if msg.grouped_id:
        async for grouped_msg in client.iter_messages(chat_id, min_id=msg.id-10, max_id=msg.id+10):
            if grouped_msg.grouped_id == msg.grouped_id and grouped_msg.text:
                name = sanitize_filename(grouped_msg.text.split('\n')[0][:10].strip())
                if name:
                    return f"{name}-{msg_id}"
        return f"{msg_id}-media_{msg.grouped_id}"
    
    # 如果是单个消息且有文本
    if msg.text:
        name = sanitize_filename(msg.text.split('\n')[0][:10].strip(), use_underscore=True)
        if name:
            return f"{msg_id}-{name}"
    
    return f"{msg_id}-media"

def create_download_dir(base_dir: Optional[str], message_dir: str, is_reply: bool = False) -> str:
    """创建下载目录
    Args:
        base_dir: 基础下载目录，可选
        message_dir: 消息目录
        is_reply: 是否是回复目录
    Returns:
        str: 实际的下载目录路径
    """
    from src.client import download_config
    
    # 确定下载目录
    if is_reply and download_config['separate_reply_folder']:
        download_dir = os.path.join(message_dir, 'replies')
    else:
        download_dir = message_dir
    
    # 创建目录如果不存在
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    return download_dir
