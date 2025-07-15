"""
Configuration data models for type-safe configuration access.
"""

from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class BotConfig:
    """Bot configuration settings."""
    response_rate: float = 1.0
    context_length: int = 20
    initial_history_cutoff: int = 5
    my_nickname: str = "RTAR Assistant"


@dataclass
class RealityConfig:
    """REALITY App connection settings."""
    media_id: int = 0
    v_live_id: str = ""
    gid: str = ""
    auth: str = ""


@dataclass
class OpenAIConfig:
    """OpenAI API configuration using free QwQ-32B from suanli.cn"""
    api_key: str = "sk-W0rpStc95T7JVYVwDYc29IyirjtpPPby6SozFMQr17m8KWeo"
    api_base: str = "https://api.suanli.cn/v1"
    model: str = "free:QwQ-32B"
    temperature: float = 0.7


@dataclass
class ADBConfig:
    """ADB configuration for device control."""
    host: str = "127.0.0.1"
    port: str = "5555"
    input_box_x: int = 0
    input_box_y: int = 0
    send_button_x: int = 0
    send_button_y: int = 0
    auto_send: bool = True
    send_delay_min: float = 1.0
    send_delay_max: float = 3.0


@dataclass
class PerformanceConfig:
    """Performance configuration."""
    max_workers: int = 4
    response_timeout: int = 30


@dataclass
class HealthConfig:
    """Health check configuration."""
    activity_timeout: int = 10


@dataclass
class AppConfig:
    """Complete application configuration."""
    debug: bool = False
    bot: Optional[BotConfig] = field(default_factory=lambda: None)
    reality: Optional[RealityConfig] = field(default_factory=lambda: None)
    openai: Optional[OpenAIConfig] = field(default_factory=lambda: None)
    adb: Optional[ADBConfig] = field(default_factory=lambda: None)
    performance: Optional[PerformanceConfig] = field(default_factory=lambda: None)
    health: Optional[HealthConfig] = field(default_factory=lambda: None)
    
    def __post_init__(self):
        """Initialize nested configs if not provided."""
        if self.bot is None:
            self.bot = BotConfig()
        if self.reality is None:
            self.reality = RealityConfig()
        if self.openai is None:
            self.openai = OpenAIConfig()
        if self.adb is None:
            self.adb = ADBConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.health is None:
            self.health = HealthConfig()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        """Create AppConfig from dictionary."""
        return cls(
            debug=data.get('debug', {}).get('value', False),
            bot=BotConfig(
                response_rate=data.get('bot', {}).get('responseRate', {}).get('value', 1.0),
                context_length=data.get('bot', {}).get('contextLength', {}).get('value', 20),
                initial_history_cutoff=data.get('bot', {}).get('initialHistoryCutoff', {}).get('value', 5),
                my_nickname=data.get('bot', {}).get('myNickname', {}).get('value', 'RTAR Assistant')
            ),
            reality=RealityConfig(
                media_id=data.get('reality', {}).get('mediaId', {}).get('value', 0),
                v_live_id=data.get('reality', {}).get('vLiveId', {}).get('value', ''),
                gid=data.get('reality', {}).get('gid', {}).get('value', ''),
                auth=data.get('reality', {}).get('auth', {}).get('value', '')
            ),
            openai=OpenAIConfig(
                api_key=data.get('openai', {}).get('apiKey', {}).get('value', 'sk-W0rpStc95T7JVYVwDYc29IyirjtpPPby6SozFMQr17m8KWeo'),
                api_base=data.get('openai', {}).get('apiBase', {}).get('value', 'https://api.suanli.cn/v1'),
                model=data.get('openai', {}).get('model', {}).get('value', 'free:QwQ-32B'),
                temperature=data.get('openai', {}).get('temperature', {}).get('value', 0.7)
            ),
            adb=ADBConfig(
                host=data.get('adb', {}).get('host', {}).get('value', '127.0.0.1'),
                port=data.get('adb', {}).get('port', {}).get('value', '5555'),
                input_box_x=data.get('adb', {}).get('inputBox', {}).get('x', {}).get('value', 0),
                input_box_y=data.get('adb', {}).get('inputBox', {}).get('y', {}).get('value', 0),
                send_button_x=data.get('adb', {}).get('sendButton', {}).get('x', {}).get('value', 0),
                send_button_y=data.get('adb', {}).get('sendButton', {}).get('y', {}).get('value', 0),
                auto_send=data.get('adb', {}).get('autoSend', {}).get('value', True),
                send_delay_min=data.get('adb', {}).get('sendDelay', {}).get('min', {}).get('value', 1.0),
                send_delay_max=data.get('adb', {}).get('sendDelay', {}).get('max', {}).get('value', 3.0)
            ),
            performance=PerformanceConfig(
                max_workers=data.get('performance', {}).get('maxWorkers', {}).get('value', 4),
                response_timeout=data.get('performance', {}).get('responseTimeout', {}).get('value', 30)
            ),
            health=HealthConfig(
                health_check_interval=data.get('health', {}).get('healthCheckInterval', {}).get('value', 5),
                activity_timeout=data.get('health', {}).get('activityTimeout', {}).get('value', 10),
                ping_timeout=data.get('health', {}).get('pingTimeout', {}).get('value', 2)
            )
        )