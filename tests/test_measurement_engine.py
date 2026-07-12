from __future__ import annotations

import pytest

from src.ai.measurement_engine import (
    CalibrationInput,
    MeasurementEngine,
    MeasurementKind,
    MeasurementRequest,
)


def test_measurement_request_defaults_to_all_supported_measurements() -> None:
    request = MeasurementRequest(landmarks=())

    assert request.requested_measurements == frozenset(MeasurementKind)


def test_measurement_engine_methods_explicitly_require_an_implementation() -> None:
    engine = MeasurementEngine()
    calibration_input = CalibrationInput("card", 8.56, 120.0)
    request = MeasurementRequest(landmarks=())

    with pytest.raises(NotImplementedError, match="Calibration algorithms"):
        engine.calibrate(calibration_input)

    with pytest.raises(NotImplementedError, match="Measurement algorithms"):
        engine.estimate(request)
