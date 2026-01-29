import asyncio
import logging
from typing import Any

from fastapi import WebSocket

from src.core.events.bus import EventBus
from src.core.models.events import Event, EventType

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.append(websocket)
        logger.debug(f"WebSocket connected, total: {len(self._connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self._connections:
                self._connections.remove(websocket)
        logger.debug(f"WebSocket disconnected, total: {len(self._connections)}")

    async def broadcast(self, message: dict[str, Any]) -> None:
        async with self._lock:
            dead_connections = []
            for ws in self._connections:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_connections.append(ws)

            for ws in dead_connections:
                self._connections.remove(ws)

    async def handle_event(self, event: Event) -> None:
        await self.broadcast({
            "type": event.event_type.value,
            "data": event.data,
            "timestamp": event.timestamp.isoformat(),
        })

    async def register_event_handlers(self) -> None:
        for event_type in EventType:
            await self._event_bus.subscribe(event_type, self.handle_event)
