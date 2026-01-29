GENERATE_RESPONSE_TOOL = {
    "name": "generate_response",
    "description": "Generate an AI response for a chat message",
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to respond to",
            },
            "username": {
                "type": "string",
                "description": "Username of the message sender",
            },
            "include_context": {
                "type": "boolean",
                "description": "Whether to include chat context",
                "default": True,
            },
        },
        "required": ["message", "username"],
    },
}

TTS_TOOL = {
    "name": "text_to_speech",
    "description": "Convert text to speech audio",
    "inputSchema": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to convert to speech",
            },
            "voice": {
                "type": "string",
                "description": "Voice to use (alloy, echo, fable, onyx, nova, shimmer)",
                "default": "alloy",
            },
        },
        "required": ["text"],
    },
}

ASR_TOOL = {
    "name": "speech_to_text",
    "description": "Transcribe speech audio to text",
    "inputSchema": {
        "type": "object",
        "properties": {
            "audio_base64": {
                "type": "string",
                "description": "Base64 encoded audio data",
            },
            "language": {
                "type": "string",
                "description": "Language hint (e.g., 'en', 'zh', 'ja')",
            },
        },
        "required": ["audio_base64"],
    },
}

AI_TOOLS = [GENERATE_RESPONSE_TOOL, TTS_TOOL, ASR_TOOL]
