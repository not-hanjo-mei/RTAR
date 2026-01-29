"""Event system for component communication."""

from src.core.events.bus import EventBus
from src.core.events.handlers import EventHandler, EventHandlerRegistry

__all__ = ["EventBus", "EventHandler", "EventHandlerRegistry"]
