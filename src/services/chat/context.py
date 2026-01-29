from src.core.models.message import ChatContext, ChatMessage


class ContextManager:
    def __init__(self, max_length: int = 20) -> None:
        self._context = ChatContext(max_length=max_length)

    @property
    def context(self) -> ChatContext:
        return self._context

    def add_message(self, message: ChatMessage) -> None:
        self._context.add_message(message)

    def get_recent(self, n: int = 10) -> list[ChatMessage]:
        return self._context.get_recent(n)

    def to_prompt_format(self) -> list[dict[str, str]]:
        return self._context.to_prompt_format()

    def clear(self) -> None:
        self._context.clear()

    def set_max_length(self, length: int) -> None:
        self._context.max_length = length
