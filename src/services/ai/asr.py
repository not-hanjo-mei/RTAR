import io
import logging

from openai import AsyncOpenAI

from src.core.exceptions import ASRError
from src.core.models.config import AIEndpointConfig

logger = logging.getLogger(__name__)


class ASRClient:
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

    async def transcribe(
        self,
        audio: bytes,
        *,
        language: str | None = None,
        filename: str = "audio.wav",
    ) -> str:
        try:
            audio_file = io.BytesIO(audio)
            audio_file.name = filename

            response = await self.client.audio.transcriptions.create(
                model=self._config.model,
                file=audio_file,
                language=language,
            )

            return response.text

        except Exception as e:
            logger.error(f"ASR transcription failed: {e}")
            raise ASRError(f"ASR transcription failed: {e}") from e

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None
