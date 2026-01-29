import base64

from fastapi import APIRouter
from pydantic import BaseModel

from src.api.dependencies import ContainerDep

router = APIRouter(prefix="/device", tags=["device"])


class TapRequest(BaseModel):
    x: int
    y: int


class InputRequest(BaseModel):
    text: str


class DeviceStatusResponse(BaseModel):
    connected: bool


class ScreenshotResponse(BaseModel):
    image_base64: str | None = None
    error: str | None = None


@router.post("/connect")
async def connect(container: ContainerDep) -> dict[str, bool]:
    success = await container.services.device.connect()
    return {"success": success}


@router.post("/disconnect")
async def disconnect(container: ContainerDep) -> dict[str, bool]:
    await container.services.device.disconnect()
    return {"success": True}


@router.get("/status", response_model=DeviceStatusResponse)
async def get_status(container: ContainerDep) -> DeviceStatusResponse:
    return DeviceStatusResponse(connected=container.services.device.is_connected)


@router.post("/tap")
async def tap(request: TapRequest, container: ContainerDep) -> dict[str, bool]:
    success = await container.services.device.tap(request.x, request.y)
    return {"success": success}


@router.post("/input")
async def input_text(request: InputRequest, container: ContainerDep) -> dict[str, bool]:
    success = await container.services.device.send_immediate(request.text)
    return {"success": success}


@router.get("/screenshot", response_model=ScreenshotResponse)
async def screenshot(container: ContainerDep) -> ScreenshotResponse:
    data = await container.services.device.screenshot()
    if data is None:
        return ScreenshotResponse(error="Failed to take screenshot")
    return ScreenshotResponse(image_base64=base64.b64encode(data).decode())
