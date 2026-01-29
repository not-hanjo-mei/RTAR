import asyncio
import logging
import random

from src.core.events.bus import EventBus
from src.core.models.config import ADBConfig
from src.core.models.events import EventType
from src.services.device.adb import ADBController

logger = logging.getLogger(__name__)


class DeviceService:
    def __init__(self, config: ADBConfig, event_bus: EventBus) -> None:
        self._config = config
        self._event_bus = event_bus
        self._controller = ADBController(config)
        self._message_queue: asyncio.Queue[str] = asyncio.Queue()
        self._worker_task: asyncio.Task[None] | None = None
        self._running = False

    @property
    def is_connected(self) -> bool:
        return self._controller.is_connected

    async def connect(self) -> bool:
        success = await self._controller.connect()

        if success:
            await self._event_bus.publish(EventType.ADB_CONNECTED, {})
            self._start_worker()
        else:
            await self._event_bus.publish(
                EventType.ADB_ERROR,
                {"error": "Failed to connect"},
            )

        return success

    async def disconnect(self) -> None:
        self._stop_worker()
        await self._controller.disconnect()
        await self._event_bus.publish(EventType.ADB_DISCONNECTED, {})

    def _start_worker(self) -> None:
        if self._worker_task is None or self._worker_task.done():
            self._running = True
            self._worker_task = asyncio.create_task(self._message_worker())

    def _stop_worker(self) -> None:
        self._running = False
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()

    async def _message_worker(self) -> None:
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self._message_queue.get(),
                    timeout=1.0,
                )

                min_delay, max_delay = self._config.send_delay
                delay = random.uniform(min_delay, max_delay)
                await asyncio.sleep(delay)

                success = await self._controller.send_message(message)

                if success:
                    await self._event_bus.publish(
                        EventType.RESPONSE_SENT,
                        {"message": message},
                    )
                else:
                    await self._event_bus.publish(
                        EventType.ADB_ERROR,
                        {"error": f"Failed to send: {message}"},
                    )

            except TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Message worker error: {e}")

    async def queue_message(self, message: str) -> None:
        await self._message_queue.put(message)

    async def send_immediate(self, message: str) -> bool:
        return await self._controller.send_message(message)

    async def tap(self, x: int, y: int) -> bool:
        return await self._controller.tap(x, y)

    async def screenshot(self) -> bytes | None:
        return await self._controller.screenshot()
