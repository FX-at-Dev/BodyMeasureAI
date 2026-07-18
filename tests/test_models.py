from __future__ import annotations

import json
from datetime import UTC, datetime

from src.models import (
    BodyProfile,
    CalibrationData,
    ExportFormat,
    ExportProfile,
    Landmark,
    Measurement,
    MeasurementKind,
    MeasurementResult,
    MeasurementStatus,
    PoseFrame,
    ValidationResult,
    ValidationStatus,
)


def test_models_round_trip_through_json() -> None:
    calibration = CalibrationData("card", 8.56, 120.0, 0.0713, 0.9)
    result = MeasurementResult(
        measurements=(
            Measurement(
                MeasurementKind.HEIGHT,
                175.2,
                0.92,
                MeasurementStatus.AVAILABLE,
            ),
        ),
        calibration=calibration,
    )
    pose_frame = PoseFrame(
        frame_id=1,
        captured_at=datetime(2026, 7, 12, tzinfo=UTC),
        image_width=1280,
        image_height=720,
        landmarks=(Landmark(0.5, 0.2, -0.1, 0.95),),
    )
    profile = BodyProfile("profile-1", height_cm=175.0, weight_kg=70.0)
    export_profile = ExportProfile(ExportFormat.JSON, include_pose_data=True)
    validation_result = ValidationResult(
        ValidationStatus.READY,
        "Ready",
        ("body_aligned",),
    )

    encoded = json.dumps(
        {
            "result": result.to_dict(),
            "pose_frame": pose_frame.to_dict(),
            "profile": profile.to_dict(),
            "export": export_profile.to_dict(),
            "validation": validation_result.to_dict(),
        }
    )
    decoded = json.loads(encoded)

    assert MeasurementResult.from_dict(decoded["result"]) == result
    assert PoseFrame.from_dict(decoded["pose_frame"]) == pose_frame
    assert BodyProfile.from_dict(decoded["profile"]) == profile
    assert ExportProfile.from_dict(decoded["export"]) == export_profile
    assert ValidationResult.from_dict(decoded["validation"]) == validation_result
