import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DialogueContext:
    def __init__(self):
        """初始化对话上下文管理器"""
        self.messages: List[Dict[str, Any]] = []
        self.current_session_id = None
        self.session_start_time = None
        
    def start_new_session(self) -> str:
        """开始新的对话会话"""
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start_time = datetime.now()
        self.messages = []
        logger.info(f"Started new dialogue session: {self.current_session_id}")
        return self.current_session_id
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """添加新消息到当前会话
        
        Args:
            role: 消息发送者角色 ("user" 或 "assistant")
            content: 消息内容
            metadata: 额外的消息元数据（如SQL查询、可视化信息等）
        """
        if not self.current_session_id:
            self.start_new_session()
            
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        
    def get_context_window(self, window_size: int = 5) -> List[Dict[str, Any]]:
        """获取最近的对话上下文窗口
        
        Args:
            window_size: 要返回的最近消息数量
            
        Returns:
            最近的消息列表
        """
        return self.messages[-window_size:] if self.messages else []
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """获取当前会话的所有消息"""
        return self.messages
    
    def clear_context(self):
        """清空当前会话上下文"""
        self.messages = []
        self.current_session_id = None
        self.session_start_time = None
        logger.info("Cleared dialogue context")
    
    def get_session_info(self) -> Dict[str, Any]:
        """获取当前会话信息"""
        if not self.current_session_id:
            return {"status": "no_active_session"}
            
        return {
            "session_id": self.current_session_id,
            "start_time": self.session_start_time.isoformat(),
            "message_count": len(self.messages),
            "duration": (datetime.now() - self.session_start_time).total_seconds()
        } 