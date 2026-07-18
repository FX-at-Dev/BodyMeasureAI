"""Local calibration workflows for image-to-centimeter conversion."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from src.models.calibration_data import CalibrationData, CalibrationMethod
from src.services.storage_service import StorageService


@dataclass(frozen=True)
class CalibrationResult:
    """Outcome of a calibration attempt.

    Failed attempts retain an explanatory message and never replace a valid
    persisted calibration.
    """

    calibration_data: CalibrationData | None = None
    error_message: str | None = None

    @property
    def is_calibrated(self) -> bool:
        """Whether the attempt produced a usable calibration."""
        return self.calibration_data is not None

    @property
    def centimeters_per_pixel(self) -> float | None:
        """Return the derived image scale when calibration succeeded."""
        if self.calibration_data is None:
            return None
        return self.calibration_data.centimeters_per_pixel

    @property
    def confidence(self) -> float:
        """Return calibration confidence, or zero for a failed attempt."""
        if self.calibration_data is None:
            return 0.0
        return self.calibration_data.confidence


class CalibrationManager:
    """Create, persist, and reload the active local camera calibration."""

    def __init__(self, storage_service: StorageService | None = None) -> None:
        self._storage_service = storage_service or StorageService()
        self._calibration_data = self._storage_service.load_calibration()

    @property
    def calibration_data(self) -> CalibrationData | None:
        """Return the calibration loaded for the current local device."""
        return self._calibration_data

    @property
    def is_calibrated(self) -> bool:
        """Whether a local calibration is available."""
        return self._calibration_data is not None

    def calibrate_reference_object(
        self,
        reference_name: str,
        known_length_cm: float,
        measured_length_pixels: float,
        detection_confidence: float = 1.0,
    ) -> CalibrationResult:
        """Calibrate from a visible object with a known physical length."""
        return self._calibrate(
            reference_name=reference_name,
            known_length_cm=known_length_cm,
            measured_length_pixels=measured_length_pixels,
            detection_confidence=detection_confidence,
            method=CalibrationMethod.REFERENCE_OBJECT,
        )

    def calibrate_known_height(
        self,
        known_height_cm: float,
        measured_height_pixels: float,
        pose_confidence: float = 1.0,
    ) -> CalibrationResult:
        """Calibrate from a person's supplied height and visible pixel height."""
        return self._calibrate(
            reference_name="Known height",
            known_length_cm=known_height_cm,
            measured_length_pixels=measured_height_pixels,
            detection_confidence=pose_confidence,
            method=CalibrationMethod.KNOWN_HEIGHT,
        )

    def recalibrate_reference_object(
        self,
        reference_name: str,
        known_length_cm: float,
        measured_length_pixels: float,
        detection_confidence: float = 1.0,
    ) -> CalibrationResult:
        """Replace the active calibration using a new reference-object reading."""
        return self.calibrate_reference_object(
            reference_name,
            known_length_cm,
            measured_length_pixels,
            detection_confidence,
        )

    def recalibrate_known_height(
        self,
        known_height_cm: float,
        measured_height_pixels: float,
        pose_confidence: float = 1.0,
    ) -> CalibrationResult:
        """Replace the active calibration using a new known-height reading."""
        return self.calibrate_known_height(
            known_height_cm,
            measured_height_pixels,
            pose_confidence,
        )

    def clear_calibration(self) -> bool:
        """Remove the active local calibration so a new one is required."""
        if not self._storage_service.clear_calibration():
            return False
        self._calibration_data = None
        return True

    def _calibrate(
        self,
        reference_name: str,
        known_length_cm: float,
        measured_length_pixels: float,
        detection_confidence: float,
        method: CalibrationMethod,
    ) -> CalibrationResult:
        error = _validation_error(
            reference_name,
            known_length_cm,
            measured_length_pixels,
            detection_confidence,
        )
        if error is not None:
            return CalibrationResult(error_message=error)

        calibration = CalibrationData(
            reference_name=reference_name.strip(),
            known_length_cm=known_length_cm,
            measured_length_pixels=measured_length_pixels,
            centimeters_per_pixel=known_length_cm / measured_length_pixels,
            confidence=_confidence(measured_length_pixels, detection_confidence),
            method=method,
        )
        if not self._storage_service.save_calibration(calibration):
            return CalibrationResult(
                error_message="Unable to save calibration locally."
            )

        self._calibration_data = calibration
        return CalibrationResult(calibration_data=calibration)


def _validation_error(
    reference_name: str,
    known_length_cm: float,
    measured_length_pixels: float,
    detection_confidence: float,
) -> str | None:
    if not reference_name.strip():
        return "A reference name is required."
    if not isfinite(known_length_cm) or known_length_cm <= 0:
        return "Known length must be greater than zero."
    if not isfinite(measured_length_pixels) or measured_length_pixels <= 0:
        return "Measured pixel length must be greater than zero."
    if not isfinite(detection_confidence) or not 0.0 <= detection_confidence <= 1.0:
        return "Detection confidence must be between zero and one."
    return None


def _confidence(measured_length_pixels: float, detection_confidence: float) -> float:
    """Score confidence from source quality and visible reference resolution."""
    resolution_confidence = min(measured_length_pixels / 100.0, 1.0)
    return round(detection_confidence * resolution_confidence, 3)
