from src.file_utils import get_file_name, create_download_dir
from src.config import config
import os
from typing import List, Dict, Any, Optional, Tuple

def needs_auto_index(message: Any) -> bool:
    """判断消息是否需要自动编号"""
    return message.photo or (not (message.document and hasattr(message.document, 'attributes') and 
        any(hasattr(attr, 'file_name') and attr.file_name for attr in message.document.attributes)))

async def download_media_with_index(message: Any, download_dir: str, auto_index: Optional[int] = None) -> Tuple[str, Optional[int]]:
    """下载媒体文件并处理自动编号
    Returns:
        Tuple[str, Optional[int]]: (文件路径, 下一个可用的索引)
    """
    next_index = auto_index
    if needs_auto_index(message):
        index = auto_index
        next_index = auto_index + 1 if auto_index is not None else None
    else:
        index = None
    
    file_name = get_file_name(message, index)
    path = await message.download_media(os.path.join(download_dir, file_name))
    if path:
        print(f"下载文件到: {path}")
    return path, next_index

async def save_text_content(text: str, file_path: str) -> None:
    """保存文本内容到文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"已保存文本到: {file_path}")

async def get_message_files(message: Any) -> List[Dict]:
    """获取消息中的文件信息"""
    files = []
    if message.media:
        file_name = get_file_name(message)
        files.append({
            'id': message.id,
            'name': file_name,
            'grouped_id': message.grouped_id
        })
    return files

async def download_message_files(message: Any, message_dir: str, client: Any, chat_id: int) -> int:
    """下载消息中的所有文件
    Returns:
        int: 下一个可用的自动编号
    """
    try:
        if not message.media:
            return 1

        auto_index = 1
        
        # 收集需要下载的消息
        messages_to_download = []
        if message.grouped_id:
            async for grouped_message in client.iter_messages(chat_id, min_id=message.id-10, max_id=message.id+10):
                if grouped_message.grouped_id == message.grouped_id:
                    messages_to_download.append(grouped_message)
        else:
            messages_to_download.append(message)
        
        # 串行下载文件
        for msg in messages_to_download:
            if msg.media:
                _, next_index = await download_media_with_index(msg, message_dir, auto_index)
                if next_index:
                    auto_index = next_index
        
        return auto_index
    except Exception as e:
        print(f"下载消息文件时出错: {str(e)}")
        return 1

async def process_replies(message: Any, message_dir: str, next_index: int, client: Any, chat_id: int) -> int:
    """处理消息的回复"""
    try:
        files = await get_message_files(message)
        if message.grouped_id:
            async for grouped_msg in client.iter_messages(chat_id, min_id=message.id-10, max_id=message.id+10):
                if grouped_msg.grouped_id == message.grouped_id:
                    files.extend(await get_message_files(grouped_msg))

        total_replies = 0
        auto_index = next_index
        
        for file in files:
            try:
                count = 0
                async for reply in client.iter_messages(chat_id, reply_to=file['id']):
                    count += 1
                    if reply.media:
                        download_dir = create_download_dir(None, message_dir, is_reply=True)
                        path, next_auto_index = await download_media_with_index(reply, download_dir, auto_index)
                        if next_auto_index:
                            auto_index = next_auto_index
                
                total_replies = max(total_replies, count)
            except Exception as e:
                print(f"处理回复时出错: {str(e)}")
                continue
        
        return total_replies
    except Exception as e:
        print(f"处理回复时出错: {str(e)}")
        return 0

async def get_comments_and_files(message_id: int, base_dir: str, next_index: int, client: Any, chat_id: int) -> None:
    """获取并下载评论中的文件"""
    try:
        auto_index = next_index
        async for comment in client.iter_messages(chat_id, reply_to=message_id):
            print(f"\n评论 ID: {comment.id}")
            download_dir = create_download_dir(None, base_dir, is_reply=True)
            
            if comment.text:
                preview = comment.text[:30] + '...' if len(comment.text) > 30 else comment.text
                print(f"评论内容: {preview}")
                await save_text_content(comment.text, os.path.join(download_dir, f'comment_{comment.id}.txt'))
            
            if comment.media:
                path, next_auto_index = await download_media_with_index(comment, download_dir, auto_index)
                if next_auto_index:
                    auto_index = next_auto_index
    except Exception as e:
        print(f"获取评论时出错: {str(e)}")
