"""JSON-safe body-measurement domain models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from src.models.calibration_data import CalibrationData


class MeasurementKind(StrEnum):
    """Body dimensions supported by the BodyLens workflow."""

    HEIGHT = "height"
    CHEST = "chest"
    WAIST = "waist"
    HIP = "hip"
    THIGH = "thigh"
    HAND_LENGTH = "hand_length"
    HAND_WIDTH = "hand_width"
    INSEAM = "inseam"
    HEAD_CIRCUMFERENCE = "head_circumference"


class MeasurementStatus(StrEnum):
    """Availability state for a measurement value."""

    NOT_CALCULATED = "not_calculated"
    CALIBRATION_REQUIRED = "calibration_required"
    INSUFFICIENT_LANDMARKS = "insufficient_landmarks"
    AVAILABLE = "available"


class MeasurementUnit(StrEnum):
    """Units used for measurement values."""

    CENTIMETERS = "cm"


class MeasurementSide(StrEnum):
    """Body side associated with a side-specific measurement."""

    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class Measurement:
    """One estimated body dimension in centimeters."""

    kind: MeasurementKind
    value_cm: float | None
    confidence: float
    status: MeasurementStatus
    unit: MeasurementUnit = MeasurementUnit.CENTIMETERS
    side: MeasurementSide | None = None
    validation_warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "kind": self.kind.value,
            "value_cm": self.value_cm,
            "confidence": self.confidence,
            "status": self.status.value,
            "unit": self.unit.value,
            "side": self.side.value if self.side else None,
            "validation_warnings": list(self.validation_warnings),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Measurement:
        """Create a measurement from validated JSON-compatible values."""
        return cls(
            kind=MeasurementKind(data["kind"]),
            value_cm=_optional_float(data.get("value_cm")),
            confidence=float(data["confidence"]),
            status=MeasurementStatus(data["status"]),
            unit=MeasurementUnit(data.get("unit", MeasurementUnit.CENTIMETERS)),
            side=_optional_side(data.get("side")),
            validation_warnings=tuple(
                str(warning) for warning in data.get("validation_warnings", [])
            ),
        )


@dataclass(frozen=True)
class MeasurementResult:
    """Measurements and optional calibration produced from one pose frame."""

    measurements: tuple[Measurement, ...]
    calibration: CalibrationData | None = None

    def get(self, kind: MeasurementKind) -> Measurement | None:
        """Return one measurement by kind, if present."""
        return next(
            (
                measurement
                for measurement in self.measurements
                if measurement.kind == kind
            ),
            None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "measurements": [
                measurement.to_dict() for measurement in self.measurements
            ],
            "calibration": self.calibration.to_dict() if self.calibration else None,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> MeasurementResult:
        """Create a result from a JSON-compatible representation."""
        calibration_data = data.get("calibration")
        return cls(
            measurements=tuple(
                Measurement.from_dict(measurement)
                for measurement in data.get("measurements", [])
            ),
            calibration=(
                CalibrationData.from_dict(calibration_data)
                if isinstance(calibration_data, Mapping)
                else None
            ),
        )


def _optional_float(value: Any) -> float | None:
    return float(value) if value is not None else None


def _optional_side(value: Any) -> MeasurementSide | None:
    return MeasurementSide(value) if value is not None else None
