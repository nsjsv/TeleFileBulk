import json
import os
from typing import Optional, Set

class CheckpointManager:
    """管理下载检查点的类，用于记录已处理的消息和群组"""
    
    def __init__(self, checkpoint_file: str = "checkpoint.json"):
        self.checkpoint_file: str = checkpoint_file
        self.processed_groups: Set[int] = set()
        self.last_message_id: Optional[int] = None
        self._load_checkpoint()
    
    def _load_checkpoint(self) -> None:
        """从文件加载检查点信息"""
        if not os.path.exists(self.checkpoint_file):
            return
            
        try:
            with open(self.checkpoint_file, 'r') as f:
                data = json.load(f)
                self.processed_groups = set(data.get('processed_groups', []))
                self.last_message_id = data.get('last_message_id')
            
            if self.last_message_id:
                print(f"已加载检查点: 上次处理到消息ID {self.last_message_id}, "
                      f"已处理 {len(self.processed_groups)} 个群组")
        except Exception as e:
            print(f"加载检查点文件失败: {str(e)}")
    
    def _save_checkpoint(self) -> None:
        """保存检查点信息到文件"""
        try:
            data = {
                'processed_groups': list(self.processed_groups),
                'last_message_id': self.last_message_id
            }
            with open(self.checkpoint_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"保存检查点文件失败: {str(e)}")
    
    def add_processed_group(self, grouped_id: Optional[int], message_id: int) -> None:
        """添加已处理的群组ID和最新消息ID
        Args:
            grouped_id: 群组ID，可能为None
            message_id: 消息ID
        """
        if grouped_id is not None:
            self.processed_groups.add(grouped_id)
        self.last_message_id = message_id
        self._save_checkpoint()
    
    def is_group_processed(self, grouped_id: Optional[int]) -> bool:
        """检查群组是否已处理
        Args:
            grouped_id: 群组ID
        Returns:
            bool: 如果群组已处理返回True，否则返回False
        """
        return grouped_id is not None and grouped_id in self.processed_groups
    
    def get_start_message_id(self) -> Optional[int]:
        """获取开始消息ID
        Returns:
            Optional[int]: 上次处理的最后一条消息ID，如果没有则返回None
        """
        return self.last_message_id
