class RTARError(Exception):
    pass


class ConfigError(RTARError):
    pass


class ConnectionError(RTARError):
    pass


class WebSocketError(ConnectionError):
    pass


class ADBError(ConnectionError):
    pass


class AIServiceError(RTARError):
    pass


class LLMError(AIServiceError):
    pass


class TTSError(AIServiceError):
    pass


class ASRError(AIServiceError):
    pass
