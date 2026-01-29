CHAT_RESPONSE_PROMPT = {
    "name": "chat_response",
    "description": "Generate a response to a chat message",
    "arguments": [
        {
            "name": "message",
            "description": "The message to respond to",
            "required": True,
        },
        {
            "name": "username",
            "description": "Username of the sender",
            "required": True,
        },
        {
            "name": "style",
            "description": "Response style (friendly, formal, playful)",
            "required": False,
        },
    ],
}

GREETING_PROMPT = {
    "name": "greeting",
    "description": "Generate a greeting message",
    "arguments": [
        {
            "name": "username",
            "description": "Username to greet",
            "required": False,
        },
    ],
}

ALL_PROMPTS = [CHAT_RESPONSE_PROMPT, GREETING_PROMPT]
