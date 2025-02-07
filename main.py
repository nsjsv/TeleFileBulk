import os
from src.client import client, CHAT_ID
from src.file_utils import get_folder_name
from src.message_utils import download_message_files, process_replies, get_comments_and_files
from src.checkpoint_manager import CheckpointManager

async def main():
    """主函数：处理消息、下载文件和评论"""
    print("正在获取消息及评论数...")
    base_download_dir = "downloads"
    if not os.path.exists(base_download_dir):
        os.makedirs(base_download_dir)
    
    # 初始化检查点管理器
    checkpoint_manager = CheckpointManager()
    
    # 获取开始消息ID
    start_id = checkpoint_manager.get_start_message_id()
    print(f"从消息ID {start_id if start_id else '最新'} 开始处理...")
    
    # 如果start_id为None，不传入offset_id参数
    if start_id is not None:
        messages = client.iter_messages(CHAT_ID, offset_id=start_id)
    else:
        messages = client.iter_messages(CHAT_ID)
    
    async for message in messages:
        try:
            # 如果消息有文本，显示前30个字符
            if message.text:
                preview = message.text[:30] + '...' if len(message.text) > 30 else message.text
                print(f"\n消息内容预览: {preview}")
            
            # 如果是群组消息且已处理过，跳过
            if message.grouped_id and checkpoint_manager.is_group_processed(message.grouped_id):
                continue
            
            # 如果消息有文本或包含媒体文件
            if message.text or message.media:
                # 获取文件夹名称
                folder_name = await get_folder_name(message, client, CHAT_ID)
                message_dir = os.path.join(base_download_dir, folder_name)
                if not os.path.exists(message_dir):
                    os.makedirs(message_dir)
                
                # 如果消息包含媒体文件
                if message.media:
                    # 下载文件并获取下一个可用的索引
                    next_index = await download_message_files(message, message_dir, client, CHAT_ID)
                    
                    # 处理评论和回复，使用下一个可用的索引
                    try:
                        replies_count = await process_replies(message, message_dir, next_index, client, CHAT_ID)
                        if replies_count > 0:
                            print(f"消息ID: {message.id} | 评论数: {replies_count}")
                        await get_comments_and_files(message.id, message_dir, next_index, client, CHAT_ID)
                    except Exception as e:
                        print(f"处理评论和回复时出错: {str(e)}")
                
                # 保存消息的文本
                message_text = message.text
                
                # 如果是群组消息，遍历同组的所有消息找文本
                if message.grouped_id and not message_text:
                    async for grouped_message in client.iter_messages(CHAT_ID, min_id=message.id-10, max_id=message.id+10):
                        if grouped_message.grouped_id == message.grouped_id and grouped_message.text:
                            message_text = grouped_message.text
                            break
                
                # 如果找到了文本，就保存
                if message_text:
                    message_text_file = os.path.join(message_dir, 'message.txt')
                    with open(message_text_file, 'w', encoding='utf-8') as f:
                        f.write(message_text)
                    print(f"已保存消息文本到: {message_text_file}")
                
                # 如果是群组消息，记录已处理
                checkpoint_manager.add_processed_group(message.grouped_id, message.id)
            
        except Exception as e:
            print(f"处理消息时出错: {str(e)}")
            continue

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())