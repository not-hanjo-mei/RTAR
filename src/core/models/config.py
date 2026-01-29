from pydantic import BaseModel, Field


class AIEndpointConfig(BaseModel):
    api_base: str
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 8192
    timeout: int = 30


class AIServicesConfig(BaseModel):
    llm: AIEndpointConfig
    tts: AIEndpointConfig | None = None
    asr: AIEndpointConfig | None = None

    def get_tts_config(self) -> AIEndpointConfig:
        return self.tts or self.llm.model_copy(update={"model": "tts-1"})

    def get_asr_config(self) -> AIEndpointConfig:
        return self.asr or self.llm.model_copy(update={"model": "whisper-1"})


class RealityConfig(BaseModel):
    media_id: int
    vlive_id: str
    gid: str
    auth: str


class ADBConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5555
    input_box: tuple[int, int] = (540, 1800)
    send_button: tuple[int, int] = (980, 1800)
    auto_send: bool = True
    send_delay: tuple[float, float] = (1.0, 3.0)


class BotConfig(BaseModel):
    nickname: str = "RTAR Assistant"
    vlive_id: str | None = None
    response_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    context_length: int = 20


class AppConfig(BaseModel):
    reality: RealityConfig
    ai: AIServicesConfig
    adb: ADBConfig = Field(default_factory=ADBConfig)
    bot: BotConfig = Field(default_factory=BotConfig)
    log_level: str = "WARNING"
