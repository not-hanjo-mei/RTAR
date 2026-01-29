from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(Enum):
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_PROCESSED = "message.processed"
    RESPONSE_GENERATED = "response.generated"
    RESPONSE_SENT = "response.sent"

    WS_CONNECTED = "ws.connected"
    WS_DISCONNECTED = "ws.disconnected"
    WS_ERROR = "ws.error"

    ADB_CONNECTED = "adb.connected"
    ADB_DISCONNECTED = "adb.disconnected"
    ADB_ERROR = "adb.error"

    LLM_REQUEST = "llm.request"
    LLM_RESPONSE = "llm.response"
    TTS_REQUEST = "tts.request"
    TTS_COMPLETE = "tts.complete"
    ASR_REQUEST = "asr.request"
    ASR_COMPLETE = "asr.complete"

    BOT_STARTED = "bot.started"
    BOT_STOPPED = "bot.stopped"
    BOT_ERROR = "bot.error"


class Event(BaseModel):
    event_type: EventType
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
