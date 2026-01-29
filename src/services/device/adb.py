import asyncio
import base64
import logging
import random

from src.core.exceptions import ADBError
from src.core.models.config import ADBConfig

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 85


class ADBController:
    def __init__(self, config: ADBConfig) -> None:
        self._config = config
        self._connected = False
        self._device_address = f"{config.host}:{config.port}"

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def _run_adb(self, *args: str) -> tuple[int, str, str]:
        cmd = ["adb", "-s", self._device_address, *args]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            return (
                proc.returncode or 0,
                stdout.decode("utf-8", errors="replace"),
                stderr.decode("utf-8", errors="replace"),
            )
        except TimeoutError as e:
            raise ADBError("ADB command timed out") from e
        except Exception as e:
            raise ADBError(f"ADB command failed: {e}") from e

    async def connect(self) -> bool:
        code, stdout, stderr = await self._run_adb("connect", self._device_address)

        if code == 0 and ("connected" in stdout.lower() or "already connected" in stdout.lower()):
            self._connected = True
            logger.info(f"Connected to device: {self._device_address}")
            return True

        logger.error(f"Failed to connect: {stdout} {stderr}")
        return False

    async def disconnect(self) -> None:
        if self._connected:
            await self._run_adb("disconnect", self._device_address)
            self._connected = False
            logger.info(f"Disconnected from device: {self._device_address}")

    async def tap(self, x: int, y: int) -> bool:
        code, _, stderr = await self._run_adb("shell", "input", "tap", str(x), str(y))
        if code != 0:
            logger.error(f"Tap failed: {stderr}")
            return False
        return True

    async def input_text(self, text: str) -> bool:
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")

        broadcast_cmd = f"am broadcast -a ADB_INPUT_B64 --es msg '{encoded}'"

        code, _, stderr = await self._run_adb("shell", broadcast_cmd)
        if code != 0:
            logger.error(f"Input text failed: {stderr}")
            return False
        return True

    async def screenshot(self) -> bytes | None:
        code, stdout, stderr = await self._run_adb("exec-out", "screencap", "-p")

        if code != 0:
            logger.error(f"Screenshot failed: {stderr}")
            return None

        return stdout.encode("latin-1")

    async def send_message(self, text: str) -> bool:
        if len(text) > MAX_MESSAGE_LENGTH:
            return await self._send_long_message(text)
        return await self._send_single_message(text)

    async def _send_single_message(self, text: str) -> bool:
        x, y = self._config.input_box
        await self.tap(x, y)
        await asyncio.sleep(0.3)

        if not await self.input_text(text):
            return False

        if self._config.auto_send:
            await asyncio.sleep(0.2)
            sx, sy = self._config.send_button
            await self.tap(sx, sy)

        return True

    async def _send_long_message(self, text: str) -> bool:
        parts = self._split_text(text, MAX_MESSAGE_LENGTH)

        for i, part in enumerate(parts):
            if i > 0:
                await asyncio.sleep(random.uniform(0.25, 0.5))

            if not await self._send_single_message(part):
                return False

        return True

    def _split_text(self, text: str, max_length: int) -> list[str]:
        if len(text) <= max_length:
            return [text]

        parts: list[str] = []
        breakpoints = ["。", ".", "，", ",", "！", "!", "？", "?", " ", ":", ";"]

        while text:
            if len(text) <= max_length:
                parts.append(text.strip())
                break

            split_pos = max_length
            for bp in breakpoints:
                pos = text.rfind(bp, max_length // 2, max_length)
                if pos != -1:
                    split_pos = pos + 1
                    break

            part = text[:split_pos].strip()
            if part:
                parts.append(part)
            text = text[split_pos:].strip()

        return parts
