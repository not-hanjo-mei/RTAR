# -*- coding: utf-8 -*-

import asyncio
import sys

import uvicorn


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
        host="0.0.0.0",
        port=7860,
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

    app = gr.mount_gradio_app(fastapi_app, gradio_app, path="/ui", theme='CultriX/gradio-theme')

    uv_level = app_config.log_level.lower()
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=7860,
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
            asyncio.run(run_with_ui())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
