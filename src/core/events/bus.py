import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

from src.core.models.events import Event, EventType

EventHandler = Callable[[Event], Coroutine[Any, Any, None]]

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventHandler]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        async with self._lock:
            if handler not in self._handlers[event_type]:
                self._handlers[event_type].append(handler)
                logger.debug(f"Subscribed {handler.__name__} to {event_type.value}")

    async def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        async with self._lock:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Unsubscribed {handler.__name__} from {event_type.value}")

    async def publish(self, event_type: EventType, data: dict[str, Any] | None = None) -> None:
        event = Event(event_type=event_type, data=data or {})
        handlers = self._handlers.get(event_type, [])

        if not handlers:
            logger.debug(f"No handlers for {event_type.value}")
            return

        tasks = [self._safe_call(handler, event) for handler in handlers]
        await asyncio.gather(*tasks)

    async def _safe_call(self, handler: EventHandler, event: Event) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Handler {handler.__name__} failed for {event.event_type.value}: {e}")

    def clear(self) -> None:
        self._handlers.clear()
