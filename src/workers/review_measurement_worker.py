"""Threaded height and hand estimation for the review workflow."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, QThread, Signal

from src.ai.measurement_engine import MeasurementEngine
from src.models.calibration_data import CalibrationData
from src.models.measurement import Measurement


class ReviewMeasurementWorker(QThread):
    """Calculate review measurements without blocking the Qt GUI thread."""

    measurements_ready = Signal(object)
    measurement_failed = Signal(str)

    def __init__(
        self,
        landmarks: tuple[Any, ...],
        image_width_pixels: int,
        image_height_pixels: int,
        calibration: CalibrationData | None,
        measurement_engine: MeasurementEngine | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._landmarks = landmarks
        self._image_width_pixels = image_width_pixels
        self._image_height_pixels = image_height_pixels
        self._calibration = calibration
        self._measurement_engine = measurement_engine or MeasurementEngine()

    def run(self) -> None:
        """Calculate all supported review measurements."""
        try:
            measurements: tuple[Measurement, ...] = (
                self._measurement_engine.estimate_height(
                    self._landmarks,
                    self._image_height_pixels,
                    self._calibration,
                ),
                *self._measurement_engine.estimate_hands(
                    self._landmarks,
                    self._image_width_pixels,
                    self._image_height_pixels,
                    self._calibration,
                ),
            )
            self.measurements_ready.emit(measurements)
        except Exception as error:
            self.measurement_failed.emit(str(error))
