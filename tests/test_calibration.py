"""Tests for local image-scale calibration and persistence."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.ai.calibration import CalibrationManager
from src.models.calibration_data import CalibrationMethod
from src.services.storage_service import StorageService


def test_reference_object_calibration_calculates_and_persists_scale(
    tmp_path: Path,
) -> None:
    storage = StorageService(tmp_path / "calibration.json")
    manager = CalibrationManager(storage)

    result = manager.calibrate_reference_object("ID card", 8.56, 120.0, 0.9)

    assert result.is_calibrated
    assert result.centimeters_per_pixel == pytest.approx(8.56 / 120.0)
    assert result.confidence == 0.9
    assert result.calibration_data is not None
    assert result.calibration_data.method == CalibrationMethod.REFERENCE_OBJECT
    assert manager.calibration_data == result.calibration_data

    reloaded = CalibrationManager(storage)

    assert reloaded.calibration_data == result.calibration_data


def test_known_height_calibration_uses_visible_height_pixels(tmp_path: Path) -> None:
    manager = CalibrationManager(StorageService(tmp_path / "calibration.json"))

    result = manager.calibrate_known_height(175.0, 700.0, 0.8)

    assert result.is_calibrated
    assert result.centimeters_per_pixel == pytest.approx(0.25)
    assert result.confidence == 0.8
    assert result.calibration_data is not None
    assert result.calibration_data.method == CalibrationMethod.KNOWN_HEIGHT


def test_failed_recalibration_preserves_existing_calibration(tmp_path: Path) -> None:
    manager = CalibrationManager(StorageService(tmp_path / "calibration.json"))
    first = manager.calibrate_reference_object("ruler", 30.0, 300.0)

    result = manager.recalibrate_known_height(175.0, 0.0)

    assert not result.is_calibrated
    assert result.error_message == "Measured pixel length must be greater than zero."
    assert manager.calibration_data == first.calibration_data


def test_calibration_can_be_cleared_for_a_new_session(tmp_path: Path) -> None:
    storage = StorageService(tmp_path / "calibration.json")
    manager = CalibrationManager(storage)
    manager.calibrate_reference_object("ruler", 30.0, 300.0)

    assert manager.clear_calibration()
    assert not manager.is_calibrated
    assert storage.load_calibration() is None
