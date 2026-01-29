from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from pydantic import ValidationError

from src.core.exceptions import ConfigError
from src.core.models.config import AppConfig

DEFAULT_CONFIG_PATH = Path("config/config.yaml")

yaml = YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.load(f)
    except Exception as e:
        raise ConfigError(f"Invalid YAML in config file: {e}") from e

    try:
        return AppConfig.model_validate(data)
    except ValidationError as e:
        raise ConfigError(f"Config validation failed: {e}") from e


def save_config(config: AppConfig, path: Path = DEFAULT_CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, encoding="utf-8") as f:
        original_data = yaml.load(f)

    new_data = config.model_dump(mode="json")

    def update_preserving_comments(original: Any, new: Any) -> Any:
        if isinstance(original, dict) and isinstance(new, dict):
            for key, value in new.items():
                if key in original:
                    original[key] = update_preserving_comments(original[key], value)
                else:
                    original[key] = value
            return original
        return new

    updated_data = update_preserving_comments(original_data, new_data)

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(updated_data, f)


class ConfigManager:
    def __init__(self, path: Path = DEFAULT_CONFIG_PATH) -> None:
        self._path = path
        self._config: AppConfig | None = None

    @property
    def config(self) -> AppConfig:
        if self._config is None:
            self._config = load_config(self._path)
        return self._config

    def reload(self) -> AppConfig:
        self._config = load_config(self._path)
        return self._config

    def save(self) -> None:
        if self._config:
            save_config(self._config, self._path)

    def update(self, key: str, value: Any) -> None:
        parts = key.split(".")
        obj: Any = self.config

        for part in parts[:-1]:
            obj = getattr(obj, part)

        setattr(obj, parts[-1], value)

    def get(self, key: str) -> Any:
        parts = key.split(".")
        obj: Any = self.config

        for part in parts:
            obj = getattr(obj, part)

        return obj
