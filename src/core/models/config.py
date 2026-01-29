from pydantic import BaseModel, Field


class AIEndpointConfig(BaseModel):
    api_base: str
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 8192
    timeout: int = 30


class TTSConfig(BaseModel):
    enabled: bool = False
    voice: str = "alloy"
    volume: float = Field(default=1.0, ge=0.0, le=1.0)
    speed: float = Field(default=1.0, ge=0.25, le=4.0)
    model: str = "tts-1"
    instructions: str | None = None
    response_types: set[str] = Field(default_factory=lambda: {"chat"})
    api_base: str | None = None
    api_key: str | None = None
    timeout: int = 30


class ASRConfig(BaseModel):
    api_base: str | None = None
    api_key: str | None = None
    model: str = "whisper-1"
    timeout: int = 30


class AIServicesConfig(BaseModel):
    llm: AIEndpointConfig
    tts: TTSConfig | None = None
    asr: ASRConfig | None = None

    def model_post_init(self, __context: object) -> None:
        if self.tts is None:
            object.__setattr__(self, "tts", TTSConfig())
        if self.asr is None:
            object.__setattr__(self, "asr", ASRConfig())

    @property
    def tts_config(self) -> TTSConfig:
        return self.tts or TTSConfig()

    @property
    def asr_config(self) -> ASRConfig:
        return self.asr or ASRConfig()

    def get_tts_endpoint(self) -> AIEndpointConfig:
        tts = self.tts_config
        return AIEndpointConfig(
            api_base=tts.api_base or self.llm.api_base,
            api_key=tts.api_key or self.llm.api_key,
            model=tts.model,
            timeout=tts.timeout,
        )

    def get_asr_endpoint(self) -> AIEndpointConfig:
        asr = self.asr_config
        return AIEndpointConfig(
            api_base=asr.api_base or self.llm.api_base,
            api_key=asr.api_key or self.llm.api_key,
            model=asr.model,
            timeout=asr.timeout,
        )


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
