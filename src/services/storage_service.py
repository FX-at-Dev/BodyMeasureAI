"""Local JSON persistence for BodyLens data that must survive restarts."""

from __future__ import annotations

import json
from os import environ
from pathlib import Path
from typing import Any

from src.models.calibration_data import CalibrationData
from src.utils.logger import logger

CALIBRATION_PATH_ENVIRONMENT_VARIABLE = "BODYLENS_CALIBRATION_PATH"
DEFAULT_CALIBRATION_FILENAME = "bodylens_calibration.json"


class StorageService:
    """Save and load the active calibration using an atomic local JSON file."""

    def __init__(self, calibration_path: Path | None = None) -> None:
        self.calibration_path = calibration_path or _default_calibration_path()

    def save_calibration(self, calibration: CalibrationData) -> bool:
        """Atomically persist calibration, returning false on filesystem failure."""
        temporary_path = self.calibration_path.with_suffix(
            f"{self.calibration_path.suffix}.tmp"
        )
        try:
            self.calibration_path.parent.mkdir(parents=True, exist_ok=True)
            with temporary_path.open("w", encoding="utf-8") as calibration_file:
                json.dump(
                    calibration.to_dict(), calibration_file, indent=2, sort_keys=True
                )
                calibration_file.write("\n")
            temporary_path.replace(self.calibration_path)
            return True
        except OSError as error:
            logger.warning(
                "Unable to save calibration to %s: %s", self.calibration_path, error
            )
            return False

    def load_calibration(self) -> CalibrationData | None:
        """Load valid calibration data, returning none for missing or invalid files."""
        if not self.calibration_path.is_file():
            return None
        try:
            with self.calibration_path.open(encoding="utf-8") as calibration_file:
                data: Any = json.load(calibration_file)
            if not isinstance(data, dict):
                raise ValueError("Calibration must contain a JSON object.")
            calibration = CalibrationData.from_dict(data)
            if not _is_valid(calibration):
                raise ValueError("Calibration values are invalid.")
            return calibration
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
            logger.warning(
                "Unable to load calibration from %s: %s", self.calibration_path, error
            )
            return None

    def clear_calibration(self) -> bool:
        """Remove the saved calibration if one exists."""
        try:
            if self.calibration_path.exists():
                self.calibration_path.unlink()
            return True
        except OSError as error:
            logger.warning(
                "Unable to remove calibration at %s: %s", self.calibration_path, error
            )
            return False


def _default_calibration_path() -> Path:
    configured_path = environ.get(CALIBRATION_PATH_ENVIRONMENT_VARIABLE)
    return (
        Path(configured_path)
        if configured_path
        else Path.cwd() / DEFAULT_CALIBRATION_FILENAME
    )


def _is_valid(calibration: CalibrationData) -> bool:
    return (
        bool(calibration.reference_name.strip())
        and calibration.known_length_cm > 0
        and calibration.measured_length_pixels > 0
        and calibration.centimeters_per_pixel is not None
        and calibration.centimeters_per_pixel > 0
        and 0.0 <= calibration.confidence <= 1.0
    )
