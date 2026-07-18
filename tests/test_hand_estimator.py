"""Tests for calibrated left and right hand measurements."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.ai.hand_estimator import HandEstimator
from src.ai.measurement_engine import MeasurementEngine, MeasurementRequest
from src.models.calibration_data import CalibrationData
from src.models.measurement import MeasurementKind, MeasurementSide, MeasurementStatus


def _landmarks() -> tuple[SimpleNamespace, ...]:
    points = [SimpleNamespace(x=0.5, y=0.5, z=0.0, visibility=0.0) for _ in range(33)]
    points[15] = SimpleNamespace(x=0.20, y=0.50, z=0.0, visibility=0.9)
    points[17] = SimpleNamespace(x=0.30, y=0.40, z=0.0, visibility=0.9)
    points[19] = SimpleNamespace(x=0.20, y=0.40, z=0.0, visibility=0.9)
    points[16] = SimpleNamespace(x=0.80, y=0.50, z=0.0, visibility=0.8)
    points[18] = SimpleNamespace(x=0.70, y=0.40, z=0.0, visibility=0.8)
    points[20] = SimpleNamespace(x=0.80, y=0.40, z=0.0, visibility=0.8)
    return tuple(points)


def _calibration() -> CalibrationData:
    return CalibrationData("ruler", 30.0, 300.0, 0.1, 0.9)


def test_hand_estimator_measures_left_and_right_hands() -> None:
    measurements = HandEstimator().estimate(_landmarks(), 1_000, 1_000, _calibration())

    left_length, left_width, right_length, right_width = measurements

    assert left_length.kind == MeasurementKind.HAND_LENGTH
    assert left_length.side == MeasurementSide.LEFT
    assert left_length.value_cm == pytest.approx(10.0)
    assert left_width.value_cm == pytest.approx(10.0)
    assert right_length.side == MeasurementSide.RIGHT
    assert right_length.value_cm == pytest.approx(10.0)
    assert right_width.value_cm == pytest.approx(10.0)
    assert right_length.confidence == pytest.approx(0.72)


def test_hand_estimator_handles_a_partially_visible_hand() -> None:
    landmarks = list(_landmarks())
    landmarks[17] = SimpleNamespace(x=0.30, y=0.40, z=0.0, visibility=0.1)

    left_length, left_width, *_ = HandEstimator().estimate(
        tuple(landmarks), 1_000, 1_000, _calibration()
    )

    assert left_length.status == MeasurementStatus.AVAILABLE
    assert left_width.value_cm is None
    assert left_width.validation_warnings == ("Left palm partially visible",)


def test_hand_estimator_reports_an_unavailable_missing_hand() -> None:
    measurements = HandEstimator().estimate((), 1_000, 1_000, _calibration())

    assert all(measurement.value_cm is None for measurement in measurements)
    assert measurements[0].validation_warnings == ("Hand not visible",)


def test_measurement_engine_returns_requested_hand_measurements() -> None:
    result = MeasurementEngine().estimate(
        MeasurementRequest(
            landmarks=_landmarks(),
            image_width_pixels=1_000,
            image_height_pixels=1_000,
            requested_measurements=frozenset(
                {MeasurementKind.HAND_LENGTH, MeasurementKind.HAND_WIDTH}
            ),
            calibration=_calibration(),
        )
    )

    assert len(result.estimates) == 4
    assert {measurement.side for measurement in result.estimates} == {
        MeasurementSide.LEFT,
        MeasurementSide.RIGHT,
    }
