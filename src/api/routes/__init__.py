from src.api.routes.ai import router as ai_router
from src.api.routes.chat import router as chat_router
from src.api.routes.config import router as config_router
from src.api.routes.device import router as device_router

__all__ = ["chat_router", "ai_router", "device_router", "config_router"]
