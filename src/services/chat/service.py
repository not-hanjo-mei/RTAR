import asyncio
import logging
from typing import Any
from uuid import uuid4

from src.core.events.bus import EventBus
from src.core.models.config import AppConfig
from src.core.models.events import EventType
from src.core.models.message import ChatMessage, MessageType
from src.services.ai.service import AIService
from src.services.chat.context import ContextManager
from src.services.chat.presets import PresetManager
from src.services.chat.processor import MessageProcessor
from src.services.chat.websocket import RealityWebSocket
from src.services.device.service import DeviceService

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        config: AppConfig,
        event_bus: EventBus,
        ai_service: AIService,
        device_service: DeviceService,
    ) -> None:
        self._config = config
        self._event_bus = event_bus
        self._ai_service = ai_service
        self._device_service = device_service

        self._websocket = RealityWebSocket(config.reality)
        self._processor = MessageProcessor(config.bot, config.reality.vlive_id)
        self._context = ContextManager(config.bot.context_length)
        self._presets = PresetManager()

        self._running = False
        self._processing_lock = asyncio.Lock()

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def context(self) -> ContextManager:
        return self._context

    async def start(self) -> None:
        if self._running:
            return

        # Start processor FIRST to set _start_time before any messages arrive
        self._processor.start()
        self._running = True

        self._websocket.set_message_callback(self._on_message)
        self._websocket.set_disconnect_callback(self._on_disconnect)

        await self._websocket.connect()
        await self._device_service.connect()

        await self._event_bus.publish(EventType.BOT_STARTED, {})
        await self._event_bus.publish(EventType.WS_CONNECTED, {})

        logger.info("Chat service started")

    async def stop(self) -> None:
        if not self._running:
            return

        self._running = False
        self._processor.stop()

        await self._websocket.disconnect()

        await self._event_bus.publish(EventType.BOT_STOPPED, {})
        await self._event_bus.publish(EventType.WS_DISCONNECTED, {})

        logger.info("Chat service stopped")

    def _add_bot_response_to_context(self, response: str) -> None:
        bot_vlive_id = self._config.bot.vlive_id or self._config.reality.vlive_id
        bot_msg = ChatMessage(
            id=str(uuid4()),
            username=bot_vlive_id or "assistant",
            display_name=self._config.bot.nickname,
            content=response,
            message_type=MessageType.ASSISTANT,
        )
        self._context.add_message(bot_msg)
        logger.debug(f"[Context] Added bot response: {response[:50]}...")

    async def _speak_response(self, response: str, response_type: str = "chat") -> None:
        if not self._config.ai.tts.enabled:
            return

        if response_type not in self._config.ai.tts.response_types:
            logger.debug(f"[TTS] Skipping TTS for response type: {response_type}")
            return

        try:
            await self._ai_service.text_to_speech(
                response,
                voice=self._config.ai.tts.voice,
                play=True,
                volume=self._config.ai.tts.volume,
            )
            logger.debug(f"[TTS] Spoke response: {response[:50]}...")
        except Exception as e:
            logger.error(f"[TTS] Failed to speak response: {e}")

    async def _on_disconnect(self, code: int, reason: str) -> None:
        logger.warning(f"[ChatService] WebSocket disconnected: code={code}, reason={reason}")

        if not self._running:
            return

        permanent_codes = {4003, 4004, 4005, 1000, 1001}
        if code in permanent_codes:
            logger.info(f"[ChatService] Permanent disconnect (code={code}), stopping bot")
            await self.stop()
            return

        logger.info("[ChatService] Connection lost, attempting to reconnect...")
        await self._event_bus.publish(EventType.WS_DISCONNECTED, {"code": code, "reason": reason})

        max_retries = 5
        retry_delays = [2, 5, 10, 15, 30]

        for attempt in range(max_retries):
            if not self._running:
                break

            delay = retry_delays[min(attempt, len(retry_delays) - 1)]
            logger.info(
                f"[ChatService] Reconnect attempt {attempt + 1}/{max_retries} in {delay}s..."
            )
            await asyncio.sleep(delay)

            try:
                await self._websocket.connect()
                logger.info("[ChatService] Reconnected successfully!")
                await self._event_bus.publish(EventType.WS_CONNECTED, {})
                return
            except Exception as e:
                logger.warning(f"[ChatService] Reconnect attempt {attempt + 1} failed: {e}")

        logger.error("[ChatService] Failed to reconnect after all attempts, stopping bot")
        await self.stop()

    async def _on_message(self, data: dict[str, Any]) -> None:
        message = self._processor.parse_message(data)
        if message is None:
            return

        await self._event_bus.publish(
            EventType.MESSAGE_RECEIVED,
            {"message": message.model_dump()},
        )

        if not self._processor.should_process(message):
            return

        await self._event_bus.publish(
            EventType.MESSAGE_PROCESSED,
            {"message": message.model_dump()},
        )

        if message.is_text:
            self._context.add_message(message)

        if not self._processor.should_respond():
            return

        async with self._processing_lock:
            if message.is_text:
                await self._generate_and_send(message)
            else:
                await self._send_preset_response(message)

    async def _generate_and_send(self, message: ChatMessage) -> None:
        try:
            context = self._context.to_prompt_format()

            response = await self._ai_service.generate_response(
                message=message.content,
                username=message.display_name,
                context=context[:-1],
            )

            await self._event_bus.publish(
                EventType.RESPONSE_GENERATED,
                {"message": message.content, "response": response},
            )

            await self._device_service.queue_message(response)
            self._add_bot_response_to_context(response)
            await self._speak_response(response, "chat")

        except Exception as e:
            logger.error(f"Failed to generate response: {e}, using fallback")
            await self._event_bus.publish(
                EventType.BOT_ERROR,
                {"error": str(e)},
            )
            fallback = self._presets.get("fallback", message.display_name)
            if fallback:
                await self._device_service.queue_message(fallback)
                self._add_bot_response_to_context(fallback)
                await self._speak_response(fallback, "fallback")

    async def _send_preset_response(self, message: ChatMessage) -> None:
        response = self._presets.get_by_type(message.message_type, message.display_name)
        if not response:
            logger.debug(f"No preset for message type: {message.message_type}")
            return

        logger.info(f"Sending preset response for {message.message_type.value}: {response}")

        await self._event_bus.publish(
            EventType.RESPONSE_GENERATED,
            {"message": message.content, "response": response, "preset": True},
        )

        await self._device_service.queue_message(response)
        self._add_bot_response_to_context(response)
        await self._speak_response(response, message.message_type.value)

    async def send_message(self, text: str) -> bool:
        success = await self._device_service.send_immediate(text)
        if success:
            self._add_bot_response_to_context(text)
            await self._speak_response(text, "manual")
        return success

    def get_stats(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "ws_connected": self._websocket.is_connected,
            "adb_connected": self._device_service.is_connected,
            "context_length": len(self._context.context.messages),
        }
