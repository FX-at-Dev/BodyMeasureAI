"""Application-wide console and rotating-file logging configuration."""

from __future__ import annotations

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from threading import RLock
from typing import TextIO

APP_LOGGER_NAME = "bodylens"
DEFAULT_LOG_FILENAME = "bodylens.log"
DEFAULT_LOG_RETENTION_DAYS = 14
_HANDLER_NAME_PREFIX = "bodylens."
_CONFIGURATION_LOCK = RLock()


class ColoredConsoleFormatter(logging.Formatter):
    """Add ANSI level colors when the active console supports them."""

    _COLORS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[1;31m",
    }
    _RESET = "\033[0m"

    def __init__(self, stream: TextIO) -> None:
        super().__init__("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        self._use_colors = stream.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record, colorizing its level when supported."""
        formatted = super().format(record)
        color = self._COLORS.get(record.levelno)

        if not self._use_colors or color is None:
            return formatted

        return f"{color}{formatted}{self._RESET}"


def get_logger() -> logging.Logger:
    """Return the singleton logger shared by every BodyLens module."""
    return logging.getLogger(APP_LOGGER_NAME)


def configure_logging(
    debug: bool = False,
    log_directory: Path | None = None,
) -> logging.Logger:
    """Configure console and daily rotating file logging once per process.

    File logging is disabled only when the log directory cannot be created; in
    that case the configured console handler continues to report the failure.
    """
    with _CONFIGURATION_LOCK:
        application_logger = get_logger()
        application_logger.setLevel(logging.DEBUG if debug else logging.INFO)
        application_logger.propagate = False
        _remove_application_handlers(application_logger)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        console_handler.setFormatter(ColoredConsoleFormatter(sys.stderr))
        _mark_application_handler(console_handler, "console")
        application_logger.addHandler(console_handler)

        try:
            file_handler = _create_file_handler(log_directory)
        except OSError as error:
            application_logger.warning("File logging is unavailable: %s", error)
        else:
            _mark_application_handler(file_handler, "file")
            application_logger.addHandler(file_handler)

        return application_logger


def _create_file_handler(log_directory: Path | None) -> TimedRotatingFileHandler:
    directory = log_directory or Path.cwd() / "logs"
    directory.mkdir(parents=True, exist_ok=True)
    handler = TimedRotatingFileHandler(
        directory / DEFAULT_LOG_FILENAME,
        when="midnight",
        interval=1,
        backupCount=DEFAULT_LOG_RETENTION_DAYS,
        encoding="utf-8",
        delay=True,
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )
    return handler


def _remove_application_handlers(application_logger: logging.Logger) -> None:
    for handler in list(application_logger.handlers):
        if (handler.get_name() or "").startswith(_HANDLER_NAME_PREFIX):
            application_logger.removeHandler(handler)
            handler.close()


def _mark_application_handler(handler: logging.Handler, handler_type: str) -> None:
    handler.set_name(f"{_HANDLER_NAME_PREFIX}{handler_type}")


logger: logging.Logger = get_logger()
