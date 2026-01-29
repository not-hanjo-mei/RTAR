import logging
from typing import Literal

from openai import AsyncOpenAI

from src.core.exceptions import TTSError
from src.core.models.config import AIEndpointConfig

logger = logging.getLogger(__name__)

VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


class TTSClient:
    def __init__(self, config: AIEndpointConfig) -> None:
        self._config = config
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url=self._config.api_base,
                api_key=self._config.api_key,
                timeout=self._config.timeout,
            )
        return self._client

    async def synthesize(
        self,
        text: str,
        *,
        voice: VoiceType = "alloy",
        speed: float = 1.0,
    ) -> bytes:
        try:
            response = await self.client.audio.speech.create(
                model=self._config.model,
                voice=voice,
                input=text,
                speed=speed,
            )

            return response.content

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise TTSError(f"TTS synthesis failed: {e}") from e

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None
