from src.mcp.tools.ai_tools import AI_TOOLS
from src.mcp.tools.chat_tools import CHAT_TOOLS
from src.mcp.tools.config_tools import CONFIG_TOOLS
from src.mcp.tools.device_tools import DEVICE_TOOLS

ALL_TOOLS = [*CHAT_TOOLS, *AI_TOOLS, *DEVICE_TOOLS, *CONFIG_TOOLS]

__all__ = ["CHAT_TOOLS", "AI_TOOLS", "DEVICE_TOOLS", "CONFIG_TOOLS", "ALL_TOOLS"]
