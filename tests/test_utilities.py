from __future__ import annotations

from src.utils.constants import APP_NAME
from src.utils.logger import APP_LOGGER_NAME, get_logger, logger


def test_application_constants_and_logger_singleton() -> None:
    assert APP_NAME == "BodyMeasureAI"
    assert get_logger() is logger
    assert logger.name == APP_LOGGER_NAME
