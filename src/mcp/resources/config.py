CONFIG_RESOURCE = {
    "uri": "rtar://config",
    "name": "Configuration",
    "description": "Current RTAR configuration",
    "mimeType": "application/json",
}

CHARACTER_RESOURCE = {
    "uri": "rtar://config/character",
    "name": "Character Prompt",
    "description": "AI character/personality prompt",
    "mimeType": "text/markdown",
}

CONFIG_RESOURCES = [CONFIG_RESOURCE, CHARACTER_RESOURCE]
