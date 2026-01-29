from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from src.core.events.bus import EventBus
from src.core.models.config import AppConfig
from src.infra.config import ConfigManager
from src.infra.logging import setup_logging

if TYPE_CHECKING:
    from src.services.ai.service import AIService
    from src.services.chat.service import ChatService
    from src.services.device.service import DeviceService


@dataclass
class ServiceContainer:
    ai: "AIService"
    chat: "ChatService"
    device: "DeviceService"


class Container:
    def __init__(self, config_path: Path = Path("config/config.yaml")) -> None:
        self._config_path = config_path
        self._config_manager: ConfigManager | None = None
        self._event_bus: EventBus | None = None
        self._services: ServiceContainer | None = None
        self._initialized = False

    @property
    def config(self) -> AppConfig:
        if self._config_manager is None:
            raise RuntimeError("Container not initialized")
        return self._config_manager.config

    @property
    def config_manager(self) -> ConfigManager:
        if self._config_manager is None:
            raise RuntimeError("Container not initialized")
        return self._config_manager

    @property
    def event_bus(self) -> EventBus:
        if self._event_bus is None:
            raise RuntimeError("Container not initialized")
        return self._event_bus

    @property
    def services(self) -> ServiceContainer:
        if self._services is None:
            raise RuntimeError("Container not initialized")
        return self._services

    async def init(self) -> None:
        if self._initialized:
            return

        self._config_manager = ConfigManager(self._config_path)
        config = self._config_manager.config

        setup_logging(log_level=config.log_level)

        self._event_bus = EventBus()

        from src.services.ai.service import AIService
        from src.services.chat.service import ChatService
        from src.services.device.service import DeviceService

        ai_service = AIService(config.ai, self._event_bus)
        device_service = DeviceService(config.adb, self._event_bus)
        chat_service = ChatService(
            config=config,
            event_bus=self._event_bus,
            ai_service=ai_service,
            device_service=device_service,
        )

        self._services = ServiceContainer(
            ai=ai_service,
            chat=chat_service,
            device=device_service,
        )

        self._initialized = True

    async def shutdown(self) -> None:
        if not self._initialized:
            return

        if self._services:
            await self._services.chat.stop()
            await self._services.device.disconnect()

        if self._event_bus:
            self._event_bus.clear()

        self._initialized = False
