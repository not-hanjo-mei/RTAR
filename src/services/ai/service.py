import logging
from pathlib import Path

from src.core.events.bus import EventBus
from src.core.models.config import AIServicesConfig
from src.core.models.events import EventType
from src.services.ai.asr import ASRClient
from src.services.ai.llm import LLMClient
from src.services.ai.tts import TTSClient, VoiceType

logger = logging.getLogger(__name__)

DEFAULT_CHARACTER_PATH = Path("config/character.md")


class AIService:
    def __init__(self, config: AIServicesConfig, event_bus: EventBus) -> None:
        self._config = config
        self._event_bus = event_bus
        self._llm = LLMClient(config.llm)
        self._tts = TTSClient(config.get_tts_config())
        self._asr = ASRClient(config.get_asr_config())
        self._character_prompt: str | None = None

    def load_character(self, path: Path = DEFAULT_CHARACTER_PATH) -> str:
        if path.exists():
            self._character_prompt = path.read_text(encoding="utf-8")
        else:
            self._character_prompt = "You are a helpful assistant."
        return self._character_prompt

    @property
    def character_prompt(self) -> str:
        if self._character_prompt is None:
            self.load_character()
        return self._character_prompt or "You are a helpful assistant."

    async def generate_response(
        self,
        message: str,
        username: str,
        context: list[dict[str, str]],
        *,
        character_prompt: str | None = None,
    ) -> str:
        await self._event_bus.publish(
            EventType.LLM_REQUEST,
            {"message": message, "username": username},
        )

        system_prompt = character_prompt or self.character_prompt

        messages = [
            {"role": "system", "content": system_prompt},
            *context,
            {"role": "user", "content": f"[{username}]: {message}"},
        ]

        response = await self._llm.generate(messages)

        await self._event_bus.publish(
            EventType.LLM_RESPONSE,
            {"message": message, "username": username, "response": response},
        )

        return response

    async def text_to_speech(
        self,
        text: str,
        *,
        voice: VoiceType = "alloy",
        speed: float = 1.0,
    ) -> bytes:
        await self._event_bus.publish(EventType.TTS_REQUEST, {"text": text})

        audio = await self._tts.synthesize(text, voice=voice, speed=speed)

        await self._event_bus.publish(EventType.TTS_COMPLETE, {"text": text})

        return audio

    async def speech_to_text(
        self,
        audio: bytes,
        *,
        language: str | None = None,
    ) -> str:
        await self._event_bus.publish(EventType.ASR_REQUEST, {})

        text = await self._asr.transcribe(audio, language=language)

        await self._event_bus.publish(EventType.ASR_COMPLETE, {"text": text})

        return text

    async def close(self) -> None:
        await self._llm.close()
        await self._tts.close()
        await self._asr.close()
