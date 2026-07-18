"""Calibrated left and right hand measurements from pose landmarks."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import hypot, isfinite
from typing import Any

from src.models.calibration_data import CalibrationData
from src.models.measurement import (
    Measurement,
    MeasurementKind,
    MeasurementSide,
    MeasurementStatus,
)


@dataclass(frozen=True)
class HandEstimator:
    """Estimate hand length and palm width for both visible sides."""

    minimum_visibility: float = 0.6
    minimum_calibration_confidence: float = 0.6

    _LEFT_INDICES = (15, 17, 19, 21)
    _RIGHT_INDICES = (16, 18, 20, 22)

    def estimate(
        self,
        landmarks: Sequence[Any] | None,
        image_width_pixels: int,
        image_height_pixels: int,
        calibration: CalibrationData | None,
    ) -> tuple[Measurement, ...]:
        """Return length and palm-width estimates for left and right hands."""
        return (
            *self._estimate_hand(
                landmarks,
                image_width_pixels,
                image_height_pixels,
                calibration,
                MeasurementSide.LEFT,
                self._LEFT_INDICES,
            ),
            *self._estimate_hand(
                landmarks,
                image_width_pixels,
                image_height_pixels,
                calibration,
                MeasurementSide.RIGHT,
                self._RIGHT_INDICES,
            ),
        )

    def _estimate_hand(
        self,
        landmarks: Sequence[Any] | None,
        image_width_pixels: int,
        image_height_pixels: int,
        calibration: CalibrationData | None,
        side: MeasurementSide,
        indices: tuple[int, int, int, int],
    ) -> tuple[Measurement, Measurement]:
        if calibration is None or not self._valid_calibration(calibration):
            return self._unavailable_pair(
                side, "Poor calibration", MeasurementStatus.CALIBRATION_REQUIRED
            )
        if not landmarks or image_width_pixels <= 0 or image_height_pixels <= 0:
            return self._unavailable_pair(side, "Hand not visible")

        wrist, pinky, index, _thumb = (
            self._visible_landmark(landmarks, index_value) for index_value in indices
        )
        if wrist is None or index is None:
            return self._unavailable_pair(
                side, f"{side.value.title()} hand partially visible"
            )

        hand_length = self._measurement(
            MeasurementKind.HAND_LENGTH,
            side,
            wrist,
            index,
            image_width_pixels,
            image_height_pixels,
            calibration,
        )
        if pinky is None:
            palm_width = self._unavailable(
                MeasurementKind.HAND_WIDTH,
                side,
                f"{side.value.title()} palm partially visible",
            )
        else:
            palm_width = self._measurement(
                MeasurementKind.HAND_WIDTH,
                side,
                index,
                pinky,
                image_width_pixels,
                image_height_pixels,
                calibration,
            )
        return hand_length, palm_width

    def _measurement(
        self,
        kind: MeasurementKind,
        side: MeasurementSide,
        first: Any,
        second: Any,
        image_width_pixels: int,
        image_height_pixels: int,
        calibration: CalibrationData,
    ) -> Measurement:
        distance_pixels = hypot(
            (float(second.x) - float(first.x)) * image_width_pixels,
            (float(second.y) - float(first.y)) * image_height_pixels,
        )
        confidence = round(
            calibration.confidence
            * min(float(first.visibility), float(second.visibility)),
            3,
        )
        warnings = ("Low hand confidence",) if confidence < 0.6 else ()
        scale = calibration.centimeters_per_pixel
        assert scale is not None
        return Measurement(
            kind=kind,
            value_cm=round(distance_pixels * scale, 1),
            confidence=confidence,
            status=MeasurementStatus.AVAILABLE,
            side=side,
            validation_warnings=warnings,
        )

    def _visible_landmark(self, landmarks: Sequence[Any], index: int) -> Any | None:
        if index >= len(landmarks):
            return None
        landmark = landmarks[index]
        x = float(getattr(landmark, "x", float("nan")))
        y = float(getattr(landmark, "y", float("nan")))
        visibility = float(getattr(landmark, "visibility", 1.0))
        if (
            not isfinite(x)
            or not isfinite(y)
            or not 0.0 <= x <= 1.0
            or not 0.0 <= y <= 1.0
            or visibility < self.minimum_visibility
        ):
            return None
        return landmark

    def _unavailable_pair(
        self,
        side: MeasurementSide,
        warning: str,
        status: MeasurementStatus = MeasurementStatus.INSUFFICIENT_LANDMARKS,
    ) -> tuple[Measurement, Measurement]:
        return (
            self._unavailable(MeasurementKind.HAND_LENGTH, side, warning, status),
            self._unavailable(MeasurementKind.HAND_WIDTH, side, warning, status),
        )

    @staticmethod
    def _unavailable(
        kind: MeasurementKind,
        side: MeasurementSide,
        warning: str,
        status: MeasurementStatus = MeasurementStatus.INSUFFICIENT_LANDMARKS,
    ) -> Measurement:
        return Measurement(
            kind=kind,
            value_cm=None,
            confidence=0.0,
            status=status,
            side=side,
            validation_warnings=(warning,),
        )

    def _valid_calibration(self, calibration: CalibrationData) -> bool:
        scale = calibration.centimeters_per_pixel
        return (
            scale is not None
            and isfinite(scale)
            and scale > 0
            and calibration.confidence >= self.minimum_calibration_confidence
        )
