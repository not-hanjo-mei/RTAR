from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from src.api.dependencies import ContainerDep

router = APIRouter(prefix="/chat", tags=["chat"])


class SendMessageRequest(BaseModel):
    message: str


class SendMessageResponse(BaseModel):
    success: bool


class ChatContextResponse(BaseModel):
    messages: list[dict[str, Any]]


class ChatStatsResponse(BaseModel):
    running: bool
    ws_connected: bool
    adb_connected: bool
    context_length: int


@router.post("/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest, container: ContainerDep) -> SendMessageResponse:
    success = await container.services.chat.send_message(request.message)
    return SendMessageResponse(success=success)


@router.get("/context", response_model=ChatContextResponse)
async def get_context(container: ContainerDep, limit: int = 20) -> ChatContextResponse:
    messages = container.services.chat.context.get_recent(limit)
    return ChatContextResponse(messages=[m.model_dump(mode="json") for m in messages])


@router.get("/stats", response_model=ChatStatsResponse)
async def get_stats(container: ContainerDep) -> ChatStatsResponse:
    stats = container.services.chat.get_stats()
    return ChatStatsResponse(**stats)


@router.delete("/history")
async def clear_history(container: ContainerDep) -> dict[str, bool]:
    container.services.chat.context.clear()
    return {"success": True}
