import asyncio
import json
import logging
import ssl
from collections.abc import Callable, Coroutine
from typing import Any

import websockets
from websockets.client import WebSocketClientProtocol

from src.core.exceptions import WebSocketError
from src.core.models.config import RealityConfig

logger = logging.getLogger(__name__)

MessageCallback = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]
DisconnectCallback = Callable[[int, str], Coroutine[Any, Any, None]]


class RealityWebSocket:
    REALITY_WS_URL = "wss://comment.reality.app"
    MAX_RETRIES = 3
    RETRY_DELAYS = [1.0, 2.0, 4.0]

    def __init__(self, config: RealityConfig) -> None:
        self._config = config
        self._ws: WebSocketClientProtocol | None = None
        self._running = False
        self._message_callback: MessageCallback | None = None
        self._disconnect_callback: DisconnectCallback | None = None
        self._receive_task: asyncio.Task[None] | None = None
        self._close_code: int | None = None
        self._close_reason: str = ""

    def set_message_callback(self, callback: MessageCallback) -> None:
        self._message_callback = callback

    def set_disconnect_callback(self, callback: DisconnectCallback) -> None:
        self._disconnect_callback = callback

    def _build_url(self) -> str:
        return f"{self.REALITY_WS_URL}?media_id={self._config.media_id}"

    def _build_headers(self) -> dict[str, str]:
        return {
            "X-WFLE-vLiveID": self._config.vlive_id,
            "X-WFLE-GID": self._config.gid,
            "Authorization": self._config.auth,
            "X-WFLE-CLIENT-IDENTIFIER": "viewer",
            "Accept-Charset": "UTF-8",
            "Accept": "*/*",
            "User-Agent": "ktor-client",
        }

    def _create_ssl_context(self) -> ssl.SSLContext:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context

    async def connect(self) -> None:
        if self._ws is not None:
            return

        url = self._build_url()
        headers = self._build_headers()
        ssl_context = self._create_ssl_context()

        last_error: Exception | None = None

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(
                    f"Connecting to REALITY WebSocket (attempt {attempt + 1}/{self.MAX_RETRIES})"
                )
                self._ws = await websockets.connect(
                    url,
                    additional_headers=headers,
                    ssl=ssl_context,
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=10,
                    open_timeout=30,
                )
                self._running = True
                logger.info("Connected to REALITY WebSocket")

                self._receive_task = asyncio.create_task(self._receive_loop())
                return

            except (ConnectionResetError, OSError) as e:
                last_error = e
                error_detail = str(e) if str(e) else type(e).__name__
                logger.warning(
                    f"Connection attempt {attempt + 1} failed: {type(e).__name__}: {error_detail}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAYS[attempt]
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
            except Exception as e:
                logger.error(f"WebSocket connection failed: {e}")
                raise WebSocketError(f"Connection failed: {e}") from e

        error_detail = str(last_error) if str(last_error) else type(last_error).__name__
        logger.error(f"Failed to connect after {self.MAX_RETRIES} attempts: {error_detail}")
        raise WebSocketError(
            f"Connection failed after {self.MAX_RETRIES} retries: {error_detail}"
        ) from last_error

    async def disconnect(self) -> None:
        self._running = False

        if self._receive_task:
            self._receive_task.cancel()
            self._receive_task = None

        if self._ws:
            await self._ws.close()
            self._ws = None
            logger.info("Disconnected from REALITY WebSocket")

    async def _receive_loop(self) -> None:
        while self._running and self._ws:
            try:
                message = await self._ws.recv()
                logger.info(f"[WS] Raw message received: {message[:200]}")
                data = json.loads(message)
                logger.info(f"[WS] Parsed data keys: {list(data.keys())}")

                if self._message_callback and data:
                    await self._message_callback(data)
                else:
                    logger.warning(
                        f"[WS] No callback or empty data: callback={self._message_callback is not None}, data={bool(data)}"
                    )

            except asyncio.CancelledError:
                break
            except websockets.ConnectionClosed as e:
                logger.warning(f"WebSocket connection closed: code={e.code}, reason={e.reason}")
                self._running = False
                self._ws = None
                self._close_code = e.code
                self._close_reason = e.reason
                if self._disconnect_callback:
                    asyncio.create_task(self._disconnect_callback(e.code, e.reason))
                break
            except Exception as e:
                logger.error(f"Receive error: {e}", exc_info=True)
                self._running = False
                self._ws = None
                break

    @property
    def is_connected(self) -> bool:
        return self._ws is not None and self._running

    @property
    def close_code(self) -> int | None:
        return self._close_code

    @property
    def close_reason(self) -> str:
        return self._close_reason
