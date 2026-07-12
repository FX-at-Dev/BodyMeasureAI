"""Interfaces and data contracts for future body-measurement estimation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol


class MeasurementKind(StrEnum):
    """Body dimensions supported by the BodyLens measurement workflow."""

    HEIGHT = "height"
    CHEST = "chest"
    WAIST = "waist"
    HIP = "hip"
    THIGH = "thigh"
    HAND_LENGTH = "hand_length"
    HAND_WIDTH = "hand_width"
    INSEAM = "inseam"
    HEAD_CIRCUMFERENCE = "head_circumference"


class EstimateStatus(StrEnum):
    """Lifecycle states for an individual measurement estimate."""

    NOT_CALCULATED = "not_calculated"
    CALIBRATION_REQUIRED = "calibration_required"
    INSUFFICIENT_LANDMARKS = "insufficient_landmarks"
    AVAILABLE = "available"


class PoseLandmark(Protocol):
    """Minimal landmark contract consumed by future measurement algorithms."""

    x: float
    y: float
    z: float
    visibility: float


@dataclass(frozen=True)
class CalibrationInput:
    """Known physical reference used to calculate image scale."""

    reference_name: str
    known_length_cm: float
    measured_length_pixels: float


@dataclass(frozen=True)
class CalibrationProfile:
    """Reusable calibration result for converting image distances to centimeters."""

    reference_name: str
    centimeters_per_pixel: float
    confidence: float


@dataclass(frozen=True)
class MeasurementRequest:
    """Input data required by a future measurement-estimation algorithm."""

    landmarks: tuple[PoseLandmark, ...]
    requested_measurements: frozenset[MeasurementKind] = field(
        default_factory=lambda: frozenset(MeasurementKind)
    )
    calibration: CalibrationProfile | None = None


@dataclass(frozen=True)
class MeasurementEstimate:
    """A single normalized body-measurement result in centimeters."""

    kind: MeasurementKind
    value_cm: float | None
    confidence: float
    status: EstimateStatus


@dataclass(frozen=True)
class MeasurementResult:
    """Collection of estimates generated for one measurement request."""

    estimates: tuple[MeasurementEstimate, ...]
    calibration: CalibrationProfile | None = None

    def get(self, kind: MeasurementKind) -> MeasurementEstimate | None:
        """Return the estimate for a requested measurement kind, if available."""
        return next(
            (estimate for estimate in self.estimates if estimate.kind == kind), None
        )


class MeasurementEngine:
    """Stable interface for future calibrated body-measurement algorithms.

    Implementations must remain in the ``ai`` layer and run from a worker when
    processing live camera frames.  No estimation algorithm is provided yet.
    """

    def calibrate(self, calibration_input: CalibrationInput) -> CalibrationProfile:
        """Create a calibration profile from a known physical reference."""
        raise NotImplementedError("Calibration algorithms have not been implemented.")

    def estimate(self, request: MeasurementRequest) -> MeasurementResult:
        """Estimate requested body measurements from pose landmarks."""
        raise NotImplementedError("Measurement algorithms have not been implemented.")
