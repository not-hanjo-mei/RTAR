ADB_TAP_TOOL = {
    "name": "adb_tap",
    "description": "Tap at specific coordinates on the device screen",
    "inputSchema": {
        "type": "object",
        "properties": {
            "x": {"type": "integer", "description": "X coordinate"},
            "y": {"type": "integer", "description": "Y coordinate"},
        },
        "required": ["x", "y"],
    },
}

ADB_INPUT_TOOL = {
    "name": "adb_input",
    "description": "Input text on the device",
    "inputSchema": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to input",
            },
        },
        "required": ["text"],
    },
}

SCREENSHOT_TOOL = {
    "name": "screenshot",
    "description": "Take a screenshot of the device screen",
    "inputSchema": {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "enum": ["png", "base64"],
                "default": "base64",
            }
        },
    },
}

GET_DEVICE_STATUS_TOOL = {
    "name": "get_device_status",
    "description": "Get ADB device connection status",
    "inputSchema": {
        "type": "object",
        "properties": {},
    },
}

DEVICE_TOOLS = [ADB_TAP_TOOL, ADB_INPUT_TOOL, SCREENSHOT_TOOL, GET_DEVICE_STATUS_TOOL]
