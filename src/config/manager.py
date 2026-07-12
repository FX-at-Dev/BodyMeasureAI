"""JSON-backed application configuration management."""

from __future__ import annotations

import json
from os import environ
from pathlib import Path
from threading import Lock
from typing import Any

from src.config.settings import AppSettings
from src.utils.logger import logger

CONFIG_PATH_ENVIRONMENT_VARIABLE = "BODYLENS_CONFIG_PATH"
DEFAULT_CONFIG_FILENAME = "bodylens.json"
_CONFIGURATION_LOCK = Lock()
_configuration: ConfigurationManager | None = None


class ConfigurationManager:
    """Load and save BodyLens settings from a local JSON file."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _default_path()
        self.settings = self.load()

    def load(self) -> AppSettings:
        """Load settings from JSON, retaining safe defaults on any failure."""
        if not self.path.is_file():
            return AppSettings()

        try:
            with self.path.open(encoding="utf-8") as config_file:
                data: Any = json.load(config_file)
        except (OSError, json.JSONDecodeError) as error:
            logger.warning("Unable to load configuration from %s: %s", self.path, error)
            return AppSettings()

        if not isinstance(data, dict):
            logger.warning("Configuration at %s must contain a JSON object.", self.path)
            return AppSettings()

        return AppSettings.from_dict(data)

    def save(self, settings: AppSettings | None = None) -> bool:
        """Atomically save settings as local JSON without raising filesystem errors."""
        if settings is not None:
            self.settings = settings

        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with temporary_path.open("w", encoding="utf-8") as config_file:
                json.dump(
                    self.settings.to_dict(), config_file, indent=2, sort_keys=True
                )
                config_file.write("\n")
            temporary_path.replace(self.path)
            return True
        except OSError as error:
            logger.warning("Unable to save configuration to %s: %s", self.path, error)
            return False


def get_configuration() -> ConfigurationManager:
    """Return the lazily loaded application-wide configuration singleton."""
    global _configuration

    with _CONFIGURATION_LOCK:
        if _configuration is None:
            _configuration = ConfigurationManager()
        return _configuration


def load_settings() -> AppSettings:
    """Load application settings through the shared configuration singleton."""
    return get_configuration().settings


def _default_path() -> Path:
    configured_path = environ.get(CONFIG_PATH_ENVIRONMENT_VARIABLE)
    return (
        Path(configured_path)
        if configured_path
        else Path.cwd() / DEFAULT_CONFIG_FILENAME
    )
