from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any

from src.core.events.bus import EventBus
from src.core.models.events import Event, EventType

EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventHandlerBase(ABC):
    @abstractmethod
    async def handle(self, event: Event) -> None:
        pass


class EventHandlerRegistry:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._registered: list[tuple[EventType, EventHandler]] = []

    async def register(self, event_type: EventType, handler: EventHandler) -> None:
        await self._event_bus.subscribe(event_type, handler)
        self._registered.append((event_type, handler))

    async def unregister_all(self) -> None:
        for event_type, handler in self._registered:
            await self._event_bus.unsubscribe(event_type, handler)
        self._registered.clear()
