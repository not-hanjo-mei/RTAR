SEND_MESSAGE_TOOL = {
    "name": "send_message",
    "description": "Send a message to the REALITY chat",
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to send (max 100 chars)",
            }
        },
        "required": ["message"],
    },
}

GET_CHAT_CONTEXT_TOOL = {
    "name": "get_chat_context",
    "description": "Get recent chat messages for context",
    "inputSchema": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Number of messages to retrieve",
                "default": 20,
            }
        },
    },
}

GET_CHAT_STATS_TOOL = {
    "name": "get_chat_stats",
    "description": "Get chat service statistics",
    "inputSchema": {
        "type": "object",
        "properties": {},
    },
}

CLEAR_CHAT_HISTORY_TOOL = {
    "name": "clear_chat_history",
    "description": "Clear chat context history",
    "inputSchema": {
        "type": "object",
        "properties": {},
    },
}

CHAT_TOOLS = [
    SEND_MESSAGE_TOOL,
    GET_CHAT_CONTEXT_TOOL,
    GET_CHAT_STATS_TOOL,
    CLEAR_CHAT_HISTORY_TOOL,
]
