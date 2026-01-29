import base64

from fastapi import APIRouter
from pydantic import BaseModel

from src.api.dependencies import ContainerDep

router = APIRouter(prefix="/ai", tags=["ai"])


class GenerateRequest(BaseModel):
    message: str
    username: str
    include_context: bool = True


class GenerateResponse(BaseModel):
    response: str


class TTSRequest(BaseModel):
    text: str
    model: str = "tts-1"
    voice: str = "alloy"
    speed: float = 1.0
    instructions: str | None = None
    play: bool = False
    volume: float = 1.0


class TTSResponse(BaseModel):
    audio_base64: str


class ASRRequest(BaseModel):
    audio_base64: str
    language: str | None = None


class ASRResponse(BaseModel):
    text: str


@router.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest, container: ContainerDep) -> GenerateResponse:
    context = []
    if request.include_context:
        context = container.services.chat.context.to_prompt_format()

    response = await container.services.ai.generate_response(
        message=request.message,
        username=request.username,
        context=context,
    )
    return GenerateResponse(response=response)


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest, container: ContainerDep) -> TTSResponse:
    audio = await container.services.ai.text_to_speech(
        text=request.text,
        model=request.model,
        voice=request.voice,
        speed=request.speed,
        instructions=request.instructions,
        play=request.play,
        volume=request.volume,
    )
    return TTSResponse(audio_base64=base64.b64encode(audio).decode())


@router.post("/asr", response_model=ASRResponse)
async def speech_to_text(request: ASRRequest, container: ContainerDep) -> ASRResponse:
    audio = base64.b64decode(request.audio_base64)
    text = await container.services.ai.speech_to_text(
        audio=audio,
        language=request.language,
    )
    return ASRResponse(text=text)
