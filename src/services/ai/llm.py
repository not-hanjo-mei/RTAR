import logging

from openai import AsyncOpenAI

from src.core.exceptions import LLMError
from src.core.models.config import AIEndpointConfig

logger = logging.getLogger(__name__)


class LLMClient:
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

    async def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self._config.model,
                messages=messages,  # type: ignore
                temperature=temperature or self._config.temperature,
                max_tokens=max_tokens or self._config.max_tokens,
            )

            content = response.choices[0].message.content
            if content is None:
                raise LLMError("Empty response from LLM")

            return content

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise LLMError(f"LLM generation failed: {e}") from e

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None
