import logging
import random
from pathlib import Path

from ruamel.yaml import YAML

from src.core.models.message import MessageType

logger = logging.getLogger(__name__)

PRESETS_PATH = Path("config/presets.yaml")

MESSAGE_TYPE_TO_PRESET_KEY = {
    MessageType.JOIN: "greetings",
    MessageType.LIKE: "likes",
    MessageType.GIFT: "gift_responses",
    MessageType.FOLLOW: "follow_responses",
}


class PresetManager:
    def __init__(self, path: Path = PRESETS_PATH) -> None:
        self._path = path
        self._presets: dict[str, list[str]] = {}
        self._yaml = YAML()
        self.reload()

    def reload(self) -> None:
        if not self._path.exists():
            logger.warning(f"Presets file not found: {self._path}")
            self._presets = {}
            return

        try:
            with open(self._path, encoding="utf-8") as f:
                data = self._yaml.load(f)
                self._presets = {k: list(v) for k, v in data.items()} if data else {}
            logger.info(f"Loaded presets: {list(self._presets.keys())}")
        except Exception as e:
            logger.error(f"Failed to load presets: {e}")
            self._presets = {}

    def get(self, key: str, username: str | None = None) -> str | None:
        template = self._get_random(key)
        if template and username:
            return template.format(user=username)
        return template

    def get_by_type(self, message_type: MessageType, username: str | None = None) -> str | None:
        key = MESSAGE_TYPE_TO_PRESET_KEY.get(message_type)
        if not key:
            return None
        return self.get(key, username)

    def _get_random(self, key: str) -> str | None:
        responses = self._presets.get(key, [])
        if not responses:
            return None
        return random.choice(responses)

    @property
    def presets(self) -> dict[str, list[str]]:
        return self._presets
