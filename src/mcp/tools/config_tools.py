GET_CONFIG_TOOL = {
    "name": "get_config",
    "description": "Get current RTAR configuration",
    "inputSchema": {
        "type": "object",
        "properties": {
            "section": {
                "type": "string",
                "description": "Config section (reality, ai, adb, bot, all)",
                "enum": ["reality", "ai", "adb", "bot", "all"],
            }
        },
    },
}

SET_CONFIG_TOOL = {
    "name": "set_config",
    "description": "Update RTAR configuration",
    "inputSchema": {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Config key path (e.g., 'bot.response_rate')",
            },
            "value": {
                "description": "New value to set",
            },
        },
        "required": ["key", "value"],
    },
}

START_BOT_TOOL = {
    "name": "start_bot",
    "description": "Start the RTAR bot",
    "inputSchema": {
        "type": "object",
        "properties": {},
    },
}

STOP_BOT_TOOL = {
    "name": "stop_bot",
    "description": "Stop the RTAR bot",
    "inputSchema": {
        "type": "object",
        "properties": {},
    },
}

GET_STATUS_TOOL = {
    "name": "get_status",
    "description": "Get overall system status",
    "inputSchema": {
        "type": "object",
        "properties": {},
    },
}

CONFIG_TOOLS = [GET_CONFIG_TOOL, SET_CONFIG_TOOL, START_BOT_TOOL, STOP_BOT_TOOL, GET_STATUS_TOOL]
