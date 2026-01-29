from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from src.api.dependencies import ContainerDep

router = APIRouter(prefix="/config", tags=["config"])

CHARACTER_PATH = Path("config/character.md")
PRESETS_PATH = Path("config/presets.yaml")


class SetConfigRequest(BaseModel):
    key: str
    value: Any


class FileContentRequest(BaseModel):
    content: str


class SystemStatusResponse(BaseModel):
    running: bool
    ws_connected: bool
    adb_connected: bool


@router.get("/")
async def get_all_config(container: ContainerDep) -> dict[str, Any]:
    return container.config.model_dump(mode="json")


@router.get("/{section}")
async def get_config_section(section: str, container: ContainerDep) -> dict[str, Any]:
    return getattr(container.config, section).model_dump(mode="json")


@router.put("/")
async def update_config(request: SetConfigRequest, container: ContainerDep) -> dict[str, bool]:
    container.config_manager.update(request.key, request.value)
    container.config_manager.save()
    return {"success": True}


@router.post("/reload")
async def reload_config(container: ContainerDep) -> dict[str, bool]:
    container.config_manager.reload()
    return {"success": True}


@router.post("/control/start")
async def start_bot(container: ContainerDep) -> dict[str, bool]:
    await container.services.chat.start()
    return {"success": True}


@router.post("/control/stop")
async def stop_bot(container: ContainerDep) -> dict[str, bool]:
    await container.services.chat.stop()
    return {"success": True}


@router.get("/control/status", response_model=SystemStatusResponse)
async def get_system_status(container: ContainerDep) -> SystemStatusResponse:
    stats = container.services.chat.get_stats()
    return SystemStatusResponse(
        running=stats["running"],
        ws_connected=stats["ws_connected"],
        adb_connected=stats["adb_connected"],
    )


@router.get("/files/character")
async def get_character() -> dict[str, str]:
    if CHARACTER_PATH.exists():
        return {"content": CHARACTER_PATH.read_text(encoding="utf-8")}
    return {"content": ""}


@router.post("/files/character")
async def save_character(request: FileContentRequest) -> dict[str, bool]:
    CHARACTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHARACTER_PATH.write_text(request.content, encoding="utf-8")
    return {"success": True}


@router.get("/files/presets")
async def get_presets() -> dict[str, str]:
    if PRESETS_PATH.exists():
        return {"content": PRESETS_PATH.read_text(encoding="utf-8")}
    return {"content": ""}


@router.post("/files/presets")
async def save_presets(request: FileContentRequest) -> dict[str, bool]:
    PRESETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRESETS_PATH.write_text(request.content, encoding="utf-8")
    return {"success": True}
