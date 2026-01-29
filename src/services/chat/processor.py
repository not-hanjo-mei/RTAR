import logging
import random
from datetime import UTC, datetime
from uuid import uuid4

from src.core.models.config import BotConfig
from src.core.models.message import ChatMessage, MessageType

logger = logging.getLogger(__name__)


CONTENT_TYPE_MAP = {
    0: MessageType.SYSTEM,
    1: MessageType.TEXT,
    2: MessageType.LIKE,
    3: MessageType.GIFT,
    4: MessageType.FOLLOW,
    8: MessageType.JOIN,
    9: MessageType.SYSTEM,
}


class MessageProcessor:
    def __init__(self, config: BotConfig, reality_vlive_id: str | None = None) -> None:
        self._config = config
        self._bot_vlive_id = config.vlive_id or reality_vlive_id
        self._seen_ids: set[str] = set()
        self._start_time: float | None = None

    def start(self) -> None:
        self._start_time = datetime.now(UTC).timestamp()
        self._seen_ids.clear()
        logger.info(f"[Processor] Started at {self._start_time:.2f} (UTC)")

    def stop(self) -> None:
        self._start_time = None
        self._seen_ids.clear()

    def parse_message(self, data: dict) -> ChatMessage | None:
        msg_id = str(data.get("comment_id", data.get("id", uuid4().hex)))

        if msg_id in self._seen_ids:
            return None
        self._seen_ids.add(msg_id)

        if len(self._seen_ids) > 10000:
            self._seen_ids = set(list(self._seen_ids)[-5000:])

        content_type = data.get("content_type", 1)
        message_type = CONTENT_TYPE_MAP.get(content_type, MessageType.UNKNOWN)

        display_name = data.get("nickname", "Unknown")
        username = data.get("vlive_id", display_name)

        content = data.get("content", "")

        timestamp = self._parse_timestamp(data.get("created_at"))

        logger.debug(f"Parsed message: {display_name}: {content[:50]}")

        return ChatMessage(
            id=msg_id,
            username=username,
            display_name=display_name,
            content=content,
            message_type=message_type,
            timestamp=timestamp,
            raw_data=data,
        )

    def _parse_timestamp(self, created_at: str | int | None) -> datetime:
        if not created_at:
            return datetime.now(UTC)

        if isinstance(created_at, int):
            return datetime.fromtimestamp(created_at / 1000, tz=UTC)

        try:
            return datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return datetime.now(UTC)

    def should_process(self, message: ChatMessage) -> bool:
        if self._start_time:
            msg_timestamp = message.timestamp.timestamp()
            if msg_timestamp < self._start_time:
                logger.info(
                    f"[Processor] Ignoring old message (msg_time={msg_timestamp:.2f}, start_time={self._start_time:.2f}): "
                    f"{message.display_name}: {message.content[:30]}"
                )
                return False

        allowed_types = {
            MessageType.TEXT,
            MessageType.JOIN,
            MessageType.LIKE,
            MessageType.GIFT,
            MessageType.FOLLOW,
        }
        if message.message_type not in allowed_types:
            return False

        if self._bot_vlive_id and message.username == self._bot_vlive_id:
            logger.debug(f"[Processor] Skipping bot message: {message.display_name}")
            return False

        return True

    def should_respond(self) -> bool:
        return random.random() < self._config.response_rate
