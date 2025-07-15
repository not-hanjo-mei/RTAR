"""
Message data model.
"""

from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class MessageItem:
    """Represents a chat message with metadata."""
    
    msg: str
    sender_type: str
    name: str
    msg_id: str
    timestamp: float
    is_self: bool = False
    content_type: Optional[int] = None
    vlive_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MessageItem':
        """Create MessageItem from dictionary data."""
        return cls(
            msg=data.get('content', ''),
            sender_type=cls._get_sender_type(data.get('content_type', 1)),
            name=data.get('nickname', 'Unknown User'),
            msg_id=str(data.get('comment_id', time.time_ns())),
            timestamp=cls._parse_timestamp(data.get('created_at', '')),
            content_type=data.get('content_type', 1),
            vlive_id=data.get('vlive_id'),
            is_self=data.get('is_self', False)
        )
    
    @staticmethod
    def _get_sender_type(content_type: int) -> str:
        """Get sender type string from content type."""
        type_map = {
            0: "[Streamer]",
            1: "[  User  ]",
            2: "[  Like  ]",
            3: "[  Gift  ]",
            4: "[ Follow ]",
            8: "[  Join  ]",
            9: "[ System ]"
        }
        return type_map.get(content_type, "[  User  ]")
    
    @staticmethod
    def _parse_timestamp(created_at: str) -> float:
        """Parse ISO timestamp to Unix timestamp."""
        if not created_at:
            return time.time()
        
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            return dt.timestamp()
        except:
            return time.time()
    
    def to_dict(self) -> dict:
        """Convert MessageItem to dictionary."""
        return {
            'msg': self.msg,
            'sender_type': self.sender_type,
            'name': self.name,
            'msg_id': self.msg_id,
            'timestamp': self.timestamp,
            'is_self': self.is_self,
            'content_type': self.content_type,
            'vlive_id': self.vlive_id
        }
    
    @property
    def is_empty(self) -> bool:
        """Check if message is empty."""
        return not bool(self.msg and self.msg.strip())
    
    @property
    def is_user_message(self) -> bool:
        """Check if this is a user message."""
        return self.content_type == 1
    
    @property
    def is_system_message(self) -> bool:
        """Check if this is a system message."""
        return self.content_type in [0, 9]
    
    @property
    def is_interaction_message(self) -> bool:
        """Check if this is an interaction message (like, follow, join)."""
        return self.content_type in [2, 4, 8]