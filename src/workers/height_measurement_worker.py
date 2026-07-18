"""Threaded calibrated height estimation for the review workflow."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, QThread, Signal

from src.ai.measurement_engine import MeasurementEngine
from src.models.calibration_data import CalibrationData
from src.models.measurement import Measurement


class HeightMeasurementWorker(QThread):
    """Run height estimation outside the Qt GUI thread."""

    measurement_ready = Signal(object)
    measurement_failed = Signal(str)

    def __init__(
        self,
        landmarks: tuple[Any, ...],
        image_height_pixels: int,
        calibration: CalibrationData | None,
        measurement_engine: MeasurementEngine | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._landmarks = landmarks
        self._image_height_pixels = image_height_pixels
        self._calibration = calibration
        self._measurement_engine = measurement_engine or MeasurementEngine()

    def run(self) -> None:
        """Calculate height and report either a result or a safe error message."""
        try:
            measurement: Measurement = self._measurement_engine.estimate_height(
                self._landmarks,
                self._image_height_pixels,
                self._calibration,
            )
            self.measurement_ready.emit(measurement)
        except Exception as error:
            self.measurement_failed.emit(str(error))
