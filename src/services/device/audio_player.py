import io
import logging

import pygame

from src.core.exceptions import AudioPlaybackError

logger = logging.getLogger(__name__)


class AudioPlayer:
    def __init__(self) -> None:
        self._initialized: bool = False
        self._current_sound: pygame.mixer.Sound | None = None

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self._initialized = True
                logger.debug("AudioPlayer initialized successfully")
            except Exception as e:
                raise AudioPlaybackError(f"Failed to initialize audio: {e}") from e

    def play_audio(
        self,
        audio_data: bytes,
        audio_format: str = "mp3",
        *,
        volume: float = 1.0,
    ) -> None:
        try:
            self._ensure_initialized()
            audio_file = io.BytesIO(audio_data)
            self._current_sound = pygame.mixer.Sound(audio_file)
            self._current_sound.set_volume(max(0.0, min(1.0, volume)))
            self._current_sound.play()
            logger.debug(f"Playing audio ({len(audio_data)} bytes, volume={volume})")
        except Exception as e:
            raise AudioPlaybackError(f"Failed to play audio: {e}") from e

    def wait_until_done(self) -> None:
        if self._current_sound is not None and pygame.mixer.get_busy():
            pygame.mixer.wait()
            logger.debug("Audio playback finished")

    def stop(self) -> None:
        if pygame.mixer.get_busy():
            pygame.mixer.stop()
            logger.debug("Audio playback stopped")

    def is_playing(self) -> bool:
        return pygame.mixer.get_busy() if self._initialized else False

    def close(self) -> None:
        self.stop()
        if self._initialized:
            pygame.mixer.quit()
            self._initialized = False
            logger.debug("AudioPlayer closed")
