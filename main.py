# -*- coding: utf-8 -*-

import asyncio
import os
import sys
from pathlib import Path

import uvicorn
import colorama
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("RTAR_HOST", "0.0.0.0")
PORT = int(os.getenv("RTAR_PORT", "42069"))


async def run_web() -> None:
    from pathlib import Path

    from src.api.app import create_app
    from src.infra.config import load_config

    config_path = Path("config/config.yaml")
    app_config = load_config(config_path)

    app = create_app()
    uv_level = app_config.log_level.lower()
    config = uvicorn.Config(
        app,
        host=HOST,
        port=PORT,
        log_level=uv_level,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_mcp() -> None:
    from src.infra.container import Container
    from src.mcp.server import RTARMCPServer

    container = Container()
    await container.init()

    try:
        mcp_server = RTARMCPServer(container)
        await mcp_server.run_stdio()
    finally:
        await container.shutdown()


async def run_with_ui() -> None:
    import gradio as gr

    from pathlib import Path

    from src.api.app import create_app
    from src.infra.config import load_config
    from ui.app import create_ui

    config_path = Path("config/config.yaml")
    app_config = load_config(config_path)

    fastapi_app = create_app()
    gradio_app = create_ui()

    app = gr.mount_gradio_app(fastapi_app, gradio_app, path="/ui", theme="CultriX/gradio-theme")

    uv_level = app_config.log_level.lower()
    config = uvicorn.Config(
        app,
        host=HOST,
        port=PORT,
        log_level=uv_level,
    )
    server = uvicorn.Server(config)
    await server.serve()


def main() -> None:
    try:
        if "--mcp" in sys.argv:
            asyncio.run(run_mcp())
        elif "--no-ui" in sys.argv:
            asyncio.run(run_web())
        else:
            print(
                colorama.Fore.GREEN
                + f"Access http://localhost:{PORT}/ui in your browser to use the web UI."
                + "\n"
                + "This may take a few moments to start up."
                + "\n"
                + "Press Ctrl+C in this window to stop RTAR."
                + colorama.Style.RESET_ALL)
            asyncio.run(run_with_ui())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
