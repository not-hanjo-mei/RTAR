import base64
import json
import logging
from typing import Any

from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)

from mcp.server import Server
from src.infra.container import Container

logger = logging.getLogger(__name__)


class RTARMCPServer:
    def __init__(self, container: Container) -> None:
        self._container = container
        self._server = Server("rtar")
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        @self._server.list_tools()
        async def list_tools() -> list[Tool]:
            from src.mcp.tools import ALL_TOOLS
            return [Tool(**tool) for tool in ALL_TOOLS]

        @self._server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            result = await self._handle_tool(name, arguments)
            return [TextContent(type="text", text=json.dumps(result))]

        @self._server.list_resources()
        async def list_resources() -> list[Resource]:
            from src.mcp.resources import ALL_RESOURCES
            return [Resource(**res) for res in ALL_RESOURCES]

        @self._server.read_resource()
        async def read_resource(uri: str) -> str:
            return await self._handle_resource(uri)

        @self._server.list_prompts()
        async def list_prompts() -> list[Prompt]:
            from src.mcp.prompts import ALL_PROMPTS
            return [
                Prompt(
                    name=p["name"],
                    description=p.get("description"),
                    arguments=[
                        PromptArgument(
                            name=arg["name"],
                            description=arg.get("description"),
                            required=arg.get("required", False),
                        )
                        for arg in p.get("arguments", [])
                    ],
                )
                for p in ALL_PROMPTS
            ]

        @self._server.get_prompt()
        async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
            return await self._handle_prompt(name, arguments or {})

    async def _handle_tool(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        services = self._container.services
        config_manager = self._container.config_manager

        if name == "send_message":
            success = await services.chat.send_message(args["message"])
            return {"success": success}

        elif name == "get_chat_context":
            limit = args.get("limit", 20)
            messages = services.chat.context.get_recent(limit)
            return {"messages": [m.model_dump(mode="json") for m in messages]}

        elif name == "get_chat_stats":
            return services.chat.get_stats()

        elif name == "clear_chat_history":
            services.chat.context.clear()
            return {"success": True}

        elif name == "generate_response":
            context = []
            if args.get("include_context", True):
                context = services.chat.context.to_prompt_format()
            response = await services.ai.generate_response(
                message=args["message"],
                username=args["username"],
                context=context,
            )
            return {"response": response}

        elif name == "text_to_speech":
            audio = await services.ai.text_to_speech(
                text=args["text"],
                voice=args.get("voice", "alloy"),
            )
            return {"audio_base64": base64.b64encode(audio).decode()}

        elif name == "speech_to_text":
            audio = base64.b64decode(args["audio_base64"])
            text = await services.ai.speech_to_text(
                audio=audio,
                language=args.get("language"),
            )
            return {"text": text}

        elif name == "adb_tap":
            success = await services.device.tap(args["x"], args["y"])
            return {"success": success}

        elif name == "adb_input":
            success = await services.device.send_immediate(args["text"])
            return {"success": success}

        elif name == "screenshot":
            data = await services.device.screenshot()
            if data is None:
                return {"error": "Failed to take screenshot"}
            if args.get("format") == "base64":
                return {"image_base64": base64.b64encode(data).decode()}
            return {"image_bytes": len(data)}

        elif name == "get_device_status":
            return {"connected": services.device.is_connected}

        elif name == "get_config":
            section = args.get("section", "all")
            config = self._container.config
            if section == "all":
                return config.model_dump(mode="json")
            return getattr(config, section).model_dump(mode="json")

        elif name == "set_config":
            config_manager.update(args["key"], args["value"])
            return {"success": True}

        elif name == "start_bot":
            await services.chat.start()
            return {"success": True}

        elif name == "stop_bot":
            await services.chat.stop()
            return {"success": True}

        elif name == "get_status":
            return {
                "chat": services.chat.get_stats(),
                "device_connected": services.device.is_connected,
            }

        return {"error": f"Unknown tool: {name}"}

    async def _handle_resource(self, uri: str) -> str:
        services = self._container.services

        if uri == "rtar://chat/history":
            messages = services.chat.context.get_recent(50)
            return json.dumps([m.model_dump(mode="json") for m in messages])

        elif uri == "rtar://chat/context":
            context = services.chat.context.to_prompt_format()
            return json.dumps(context)

        elif uri == "rtar://config":
            return json.dumps(self._container.config.model_dump(mode="json"))

        elif uri == "rtar://config/character":
            return services.ai.character_prompt

        return json.dumps({"error": f"Unknown resource: {uri}"})

    async def _handle_prompt(
        self, name: str, arguments: dict[str, str]
    ) -> GetPromptResult:
        services = self._container.services

        if name == "chat_response":
            message = arguments.get("message", "")
            username = arguments.get("username", "User")
            style = arguments.get("style", "friendly")

            _ = f"{services.ai.character_prompt}\n\nRespond in a {style} manner."

            return GetPromptResult(
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Generate a response to this message from {username}: {message}",
                        ),
                    )
                ]
            )

        elif name == "greeting":
            username = arguments.get("username", "everyone")
            return GetPromptResult(
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Generate a warm greeting for {username}.",
                        ),
                    )
                ]
            )

        return GetPromptResult(messages=[])

    async def run_stdio(self) -> None:
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self._server.run(
                read_stream,
                write_stream,
                self._server.create_initialization_options(),
            )
