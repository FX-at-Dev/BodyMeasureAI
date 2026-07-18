"""Calibrated height estimation from visible MediaPipe pose landmarks."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite
from typing import Any

from src.models.calibration_data import CalibrationData
from src.models.measurement import Measurement, MeasurementKind, MeasurementStatus


@dataclass(frozen=True)
class HeightEstimator:
    """Estimate standing height from the highest head and lowest foot landmark."""

    minimum_visibility: float = 0.6
    minimum_calibration_confidence: float = 0.6
    head_crop_margin: float = 0.02
    minimum_height_pixels: float = 100.0

    _HEAD_INDICES = tuple(range(11))
    _FOOT_INDICES = (27, 28, 29, 30, 31, 32)

    def estimate(
        self,
        landmarks: Sequence[Any] | None,
        image_height_pixels: int,
        calibration: CalibrationData | None,
    ) -> Measurement:
        """Return a calibrated height with actionable validation warnings."""
        if calibration is None or not self._valid_calibration(calibration):
            return self._unavailable(
                MeasurementStatus.CALIBRATION_REQUIRED,
                "Poor calibration",
            )
        if not landmarks or image_height_pixels <= 0:
            return self._unavailable(
                MeasurementStatus.INSUFFICIENT_LANDMARKS,
                "No person detected",
            )

        head_points = self._visible_points(landmarks, self._HEAD_INDICES)
        foot_points = self._visible_points(landmarks, self._FOOT_INDICES)
        if not head_points:
            return self._unavailable(
                MeasurementStatus.INSUFFICIENT_LANDMARKS,
                "Head not visible",
            )
        if not foot_points:
            return self._unavailable(
                MeasurementStatus.INSUFFICIENT_LANDMARKS,
                "Feet not visible",
            )

        head_y = min(float(point.y) for point in head_points)
        if head_y <= self.head_crop_margin:
            return self._unavailable(
                MeasurementStatus.INSUFFICIENT_LANDMARKS,
                "Head cropped",
            )

        foot_y = max(float(point.y) for point in foot_points)
        height_pixels = (foot_y - head_y) * image_height_pixels
        if height_pixels < self.minimum_height_pixels:
            return self._unavailable(
                MeasurementStatus.INSUFFICIENT_LANDMARKS,
                "Low confidence: person is too small in frame",
            )

        landmark_confidence = sum(
            float(point.visibility) for point in (*head_points, *foot_points)
        ) / (len(head_points) + len(foot_points))
        confidence = round(calibration.confidence * landmark_confidence, 3)
        warnings: tuple[str, ...] = ()
        if confidence < self.minimum_calibration_confidence:
            warnings = ("Low confidence",)

        centimeters_per_pixel = calibration.centimeters_per_pixel
        assert centimeters_per_pixel is not None
        return Measurement(
            kind=MeasurementKind.HEIGHT,
            value_cm=round(height_pixels * centimeters_per_pixel, 1),
            confidence=confidence,
            status=MeasurementStatus.AVAILABLE,
            validation_warnings=warnings,
        )

    def _visible_points(
        self,
        landmarks: Sequence[Any],
        indices: tuple[int, ...],
    ) -> list[Any]:
        points: list[Any] = []
        for index in indices:
            if index >= len(landmarks):
                continue
            point = landmarks[index]
            y = float(getattr(point, "y", float("nan")))
            visibility = float(getattr(point, "visibility", 1.0))
            if (
                isfinite(y)
                and 0.0 <= y <= 1.0
                and visibility >= self.minimum_visibility
            ):
                points.append(point)
        return points

    @staticmethod
    def _valid_calibration(calibration: CalibrationData) -> bool:
        scale = calibration.centimeters_per_pixel
        return (
            scale is not None
            and isfinite(scale)
            and scale > 0
            and calibration.confidence >= 0.6
        )

    @staticmethod
    def _unavailable(status: MeasurementStatus, warning: str) -> Measurement:
        return Measurement(
            kind=MeasurementKind.HEIGHT,
            value_cm=None,
            confidence=0.0,
            status=status,
            validation_warnings=(warning,),
        )
