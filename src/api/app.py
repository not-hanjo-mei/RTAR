from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes import ai_router, chat_router, config_router, device_router
from src.api.websocket.handlers import WebSocketManager
from src.core.exceptions import RTARError
from src.infra.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    container = Container()
    await container.init()

    app.state.container = container
    app.state.ws_manager = WebSocketManager(container.event_bus)
    await app.state.ws_manager.register_event_handlers()

    yield

    await container.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(
        title="RTAR API",
        description="REALITY Auto Reply Tool API",
        version="2.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RTARError)
    async def rtar_exception_handler(request: Request, exc: RTARError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "error_type": type(exc).__name__},
        )

    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(ai_router, prefix="/api/v1")
    app.include_router(device_router, prefix="/api/v1")
    app.include_router(config_router, prefix="/api/v1")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.websocket("/ws/events")
    async def websocket_events(websocket: WebSocket) -> None:
        ws_manager: WebSocketManager = websocket.app.state.ws_manager
        await ws_manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await ws_manager.disconnect(websocket)

    return app
