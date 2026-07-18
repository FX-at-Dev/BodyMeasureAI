"""JSON-safe calibration model for image-to-centimeter conversion."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class CalibrationMethod(StrEnum):
    """The source used to calculate the current calibration scale."""

    REFERENCE_OBJECT = "reference_object"
    KNOWN_HEIGHT = "known_height"


@dataclass(frozen=True)
class CalibrationData:
    """Physical reference data and the resulting image scale."""

    reference_name: str
    known_length_cm: float
    measured_length_pixels: float
    centimeters_per_pixel: float | None = None
    confidence: float = 0.0
    method: CalibrationMethod = CalibrationMethod.REFERENCE_OBJECT

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "reference_name": self.reference_name,
            "known_length_cm": self.known_length_cm,
            "measured_length_pixels": self.measured_length_pixels,
            "centimeters_per_pixel": self.centimeters_per_pixel,
            "confidence": self.confidence,
            "method": self.method.value,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CalibrationData:
        """Create calibration data from a JSON-compatible representation."""
        scale = data.get("centimeters_per_pixel")
        method = data.get("method", CalibrationMethod.REFERENCE_OBJECT.value)
        return cls(
            reference_name=str(data["reference_name"]),
            known_length_cm=float(data["known_length_cm"]),
            measured_length_pixels=float(data["measured_length_pixels"]),
            centimeters_per_pixel=float(scale) if scale is not None else None,
            confidence=float(data.get("confidence", 0.0)),
            method=CalibrationMethod(method),
        )
