"""Tests for calibrated, landmark-based height estimation."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.ai.height_estimator import HeightEstimator
from src.ai.measurement_engine import MeasurementEngine, MeasurementRequest
from src.models.calibration_data import CalibrationData
from src.models.measurement import MeasurementKind, MeasurementStatus, MeasurementUnit


def _landmarks() -> tuple[SimpleNamespace, ...]:
    points = [SimpleNamespace(x=0.5, y=0.5, z=0.0, visibility=0.0) for _ in range(33)]
    points[0] = SimpleNamespace(x=0.5, y=0.10, z=0.0, visibility=0.95)
    points[27] = SimpleNamespace(x=0.45, y=0.90, z=0.0, visibility=0.90)
    points[28] = SimpleNamespace(x=0.55, y=0.92, z=0.0, visibility=0.90)
    return tuple(points)


def _calibration(confidence: float = 0.9) -> CalibrationData:
    return CalibrationData("ruler", 30.0, 300.0, 0.1, confidence)


def test_height_estimator_returns_calibrated_height_confidence_and_units() -> None:
    result = HeightEstimator().estimate(_landmarks(), 1_000, _calibration())

    assert result.kind == MeasurementKind.HEIGHT
    assert result.value_cm == pytest.approx(82.0)
    assert result.unit == MeasurementUnit.CENTIMETERS
    assert result.confidence == pytest.approx(0.825)
    assert result.status == MeasurementStatus.AVAILABLE
    assert result.validation_warnings == ()


def test_height_estimator_warns_when_feet_are_not_visible() -> None:
    landmarks = list(_landmarks())
    landmarks[27] = SimpleNamespace(x=0.45, y=0.90, z=0.0, visibility=0.1)
    landmarks[28] = SimpleNamespace(x=0.55, y=0.92, z=0.0, visibility=0.1)

    result = HeightEstimator().estimate(tuple(landmarks), 1_000, _calibration())

    assert result.value_cm is None
    assert result.status == MeasurementStatus.INSUFFICIENT_LANDMARKS
    assert result.validation_warnings == ("Feet not visible",)


def test_height_estimator_warns_when_head_is_cropped() -> None:
    landmarks = list(_landmarks())
    landmarks[0] = SimpleNamespace(x=0.5, y=0.01, z=0.0, visibility=0.95)

    result = HeightEstimator().estimate(tuple(landmarks), 1_000, _calibration())

    assert result.value_cm is None
    assert result.validation_warnings == ("Head cropped",)


def test_height_estimator_requires_good_calibration() -> None:
    result = HeightEstimator().estimate(_landmarks(), 1_000, _calibration(0.5))

    assert result.status == MeasurementStatus.CALIBRATION_REQUIRED
    assert result.validation_warnings == ("Poor calibration",)


def test_height_estimator_reports_low_landmark_confidence() -> None:
    landmarks = list(_landmarks())
    landmarks[0] = SimpleNamespace(x=0.5, y=0.10, z=0.0, visibility=0.65)
    landmarks[27] = SimpleNamespace(x=0.45, y=0.90, z=0.0, visibility=0.65)
    landmarks[28] = SimpleNamespace(x=0.55, y=0.92, z=0.0, visibility=0.65)

    result = HeightEstimator().estimate(tuple(landmarks), 1_000, _calibration())

    assert result.status == MeasurementStatus.AVAILABLE
    assert result.validation_warnings == ("Low confidence",)


def test_measurement_engine_integrates_height_estimator() -> None:
    result = MeasurementEngine().estimate(
        MeasurementRequest(
            landmarks=_landmarks(),
            image_height_pixels=1_000,
            calibration=_calibration(),
        )
    )

    height = result.get(MeasurementKind.HEIGHT)

    assert height is not None
    assert height.value_cm == pytest.approx(82.0)
    assert height.unit == MeasurementUnit.CENTIMETERS
