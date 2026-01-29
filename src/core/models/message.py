from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageType(Enum):
    TEXT = "text"
    LIKE = "like"
    GIFT = "gift"
    FOLLOW = "follow"
    JOIN = "join"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    UNKNOWN = "unknown"


class ChatMessage(BaseModel):
    id: str
    username: str
    display_name: str
    content: str
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = Field(default_factory=datetime.now)
    raw_data: dict[str, Any] | None = None

    @property
    def is_text(self) -> bool:
        return self.message_type == MessageType.TEXT

    @property
    def is_assistant(self) -> bool:
        return self.message_type == MessageType.ASSISTANT


class ChatContext(BaseModel):
    messages: list[ChatMessage] = Field(default_factory=list)
    max_length: int = 20

    def add_message(self, message: ChatMessage) -> None:
        self.messages.append(message)
        if len(self.messages) > self.max_length:
            self.messages = self.messages[-self.max_length :]

    def get_recent(self, n: int = 10) -> list[ChatMessage]:
        return self.messages[-n:]

    def to_prompt_format(self) -> list[dict[str, str]]:
        formatted = []
        for msg in self.messages:
            if msg.is_assistant:
                formatted.append({"role": "assistant", "content": msg.content})
            elif msg.is_text:
                formatted.append(
                    {"role": "user", "content": f"[{msg.display_name}]: {msg.content}"}
                )
        return formatted

    def clear(self) -> None:
        self.messages.clear()
