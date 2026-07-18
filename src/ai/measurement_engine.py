"""Height-only measurement orchestration using calibration and pose landmarks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from src.ai.hand_estimator import HandEstimator
from src.ai.height_estimator import HeightEstimator
from src.models.calibration_data import CalibrationData
from src.models.measurement import (
    Measurement,
    MeasurementKind,
    MeasurementSide,
    MeasurementStatus,
    MeasurementUnit,
)

EstimateStatus = MeasurementStatus


class PoseLandmark(Protocol):
    """Minimal landmark contract consumed by height estimation."""

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
    """Compatibility calibration contract for existing measurement callers."""

    reference_name: str
    centimeters_per_pixel: float
    confidence: float


@dataclass(frozen=True)
class MeasurementRequest:
    """Inputs needed to estimate the currently supported body measurements."""

    landmarks: tuple[PoseLandmark, ...]
    image_height_pixels: int = 0
    image_width_pixels: int = 0
    requested_measurements: frozenset[MeasurementKind] = field(
        default_factory=lambda: frozenset(MeasurementKind)
    )
    calibration: CalibrationData | CalibrationProfile | None = None


@dataclass(frozen=True)
class MeasurementEstimate:
    """Compatibility view of an individual measurement result."""

    kind: MeasurementKind
    value_cm: float | None
    confidence: float
    status: MeasurementStatus
    unit: MeasurementUnit = MeasurementUnit.CENTIMETERS
    side: MeasurementSide | None = None
    validation_warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class MeasurementResult:
    """Measurements generated for one request."""

    estimates: tuple[MeasurementEstimate, ...]
    calibration: CalibrationData | CalibrationProfile | None = None

    def get(self, kind: MeasurementKind) -> MeasurementEstimate | None:
        """Return the estimate for a requested measurement kind, if available."""
        return next(
            (estimate for estimate in self.estimates if estimate.kind == kind), None
        )


class MeasurementEngine:
    """Orchestrate calibrated height and left/right hand measurements."""

    def __init__(
        self,
        height_estimator: HeightEstimator | None = None,
        hand_estimator: HandEstimator | None = None,
    ) -> None:
        self._height_estimator = height_estimator or HeightEstimator()
        self._hand_estimator = hand_estimator or HandEstimator()

    def calibrate(self, calibration_input: CalibrationInput) -> CalibrationProfile:
        """Create a compatibility profile from a known physical reference."""
        if (
            calibration_input.known_length_cm <= 0
            or calibration_input.measured_length_pixels <= 0
        ):
            raise ValueError("Calibration lengths must be greater than zero.")
        return CalibrationProfile(
            reference_name=calibration_input.reference_name,
            centimeters_per_pixel=(
                calibration_input.known_length_cm
                / calibration_input.measured_length_pixels
            ),
            confidence=1.0,
        )

    def estimate_height(
        self,
        landmarks: tuple[PoseLandmark, ...],
        image_height_pixels: int,
        calibration: CalibrationData | None,
    ) -> Measurement:
        """Estimate calibrated standing height from one pose frame."""
        return self._height_estimator.estimate(
            landmarks,
            image_height_pixels,
            calibration,
        )

    def estimate_hands(
        self,
        landmarks: tuple[PoseLandmark, ...],
        image_width_pixels: int,
        image_height_pixels: int,
        calibration: CalibrationData | None,
    ) -> tuple[Measurement, ...]:
        """Estimate left and right hand length and palm width."""
        return self._hand_estimator.estimate(
            landmarks,
            image_width_pixels,
            image_height_pixels,
            calibration,
        )

    def estimate(self, request: MeasurementRequest) -> MeasurementResult:
        """Estimate each currently supported measurement requested by the caller."""
        calibration = self._calibration_data(request.calibration)
        measurements: list[Measurement] = []
        if MeasurementKind.HEIGHT in request.requested_measurements:
            measurements.append(
                self.estimate_height(
                    request.landmarks,
                    request.image_height_pixels,
                    calibration,
                )
            )
        if {
            MeasurementKind.HAND_LENGTH,
            MeasurementKind.HAND_WIDTH,
        } & request.requested_measurements:
            hand_measurements = self.estimate_hands(
                request.landmarks,
                request.image_width_pixels,
                request.image_height_pixels,
                calibration,
            )
            measurements.extend(
                measurement
                for measurement in hand_measurements
                if measurement.kind in request.requested_measurements
            )
        return MeasurementResult(
            estimates=tuple(
                MeasurementEstimate(
                    kind=height.kind,
                    value_cm=height.value_cm,
                    confidence=height.confidence,
                    status=height.status,
                    unit=height.unit,
                    side=height.side,
                    validation_warnings=height.validation_warnings,
                )
                for height in measurements
            ),
            calibration=request.calibration,
        )

    @staticmethod
    def _calibration_data(
        calibration: CalibrationData | CalibrationProfile | None,
    ) -> CalibrationData | None:
        if calibration is None:
            return None
        if isinstance(calibration, CalibrationData):
            return calibration
        return CalibrationData(
            reference_name=calibration.reference_name,
            known_length_cm=1.0,
            measured_length_pixels=1.0 / calibration.centimeters_per_pixel,
            centimeters_per_pixel=calibration.centimeters_per_pixel,
            confidence=calibration.confidence,
        )
