from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from src.utils.logger import configure_logging


def test_configure_logging_adds_console_and_daily_file_handlers(
    tmp_path: Path,
) -> None:
    logger = configure_logging(debug=True, log_directory=tmp_path)

    assert logger.level == logging.DEBUG
    assert any(
        isinstance(handler, logging.StreamHandler) for handler in logger.handlers
    )
    assert any(
        isinstance(handler, TimedRotatingFileHandler) for handler in logger.handlers
    )


def test_configure_logging_reuses_the_application_logger(tmp_path: Path) -> None:
    first_logger = configure_logging(log_directory=tmp_path)
    second_logger = configure_logging(log_directory=tmp_path)

    assert first_logger is second_logger
    assert (
        len(
            [
                handler
                for handler in second_logger.handlers
                if (handler.get_name() or "").startswith("bodylens.")
            ]
        )
        == 2
    )
