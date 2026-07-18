from __future__ import annotations

from types import SimpleNamespace

from src.ai.pose_validator import PoseValidator
from src.models.validation_result import ValidationStatus


def _landmarks(
    overrides: dict[int, tuple[float, float, float, float]] | None = None,
) -> list[SimpleNamespace]:
    points = [
        SimpleNamespace(x=0.5, y=0.1, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.49, y=0.09, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.51, y=0.09, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.48, y=0.1, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.52, y=0.09, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.47, y=0.1, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.53, y=0.1, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.46, y=0.12, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.54, y=0.12, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.5, y=0.13, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.5, y=0.13, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.4, y=0.3, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.6, y=0.3, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.35, y=0.45, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.65, y=0.45, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.3, y=0.55, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.7, y=0.55, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.28, y=0.6, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.72, y=0.6, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.32, y=0.62, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.68, y=0.62, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.38, y=0.64, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.62, y=0.64, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.42, y=0.7, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.58, y=0.7, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.42, y=0.78, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.58, y=0.78, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.4, y=0.82, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.6, y=0.82, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.38, y=0.88, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.62, y=0.88, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.39, y=0.93, z=0.0, visibility=1.0),
        SimpleNamespace(x=0.61, y=0.93, z=0.0, visibility=1.0),
    ]

    for index, values in (overrides or {}).items():
        x, y, z, visibility = values
        points[index] = SimpleNamespace(x=x, y=y, z=z, visibility=visibility)

    return points


def test_pose_validator_reports_ready_when_pose_is_centered() -> None:
    validator = PoseValidator()

    result = validator.validate(_landmarks(), 1280, 720)

    assert result.status == ValidationStatus.READY
    assert result.message == "Ready"
    assert result.issues == ()


def test_pose_validator_reports_missing_feet() -> None:
    validator = PoseValidator()
    landmarks = _landmarks(
        {
            27: (0.4, 0.92, 0.0, 0.2),
            28: (0.6, 0.92, 0.0, 0.2),
            29: (0.38, 0.96, 0.0, 0.2),
            30: (0.62, 0.96, 0.0, 0.2),
            31: (0.39, 0.99, 0.0, 0.2),
            32: (0.61, 0.99, 0.0, 0.2),
        }
    )

    result = validator.validate(landmarks, 1280, 720)

    assert result.status == ValidationStatus.WARNING
    assert result.message == "Feet Not Visible"


def test_pose_validator_reports_move_back_when_body_touches_frame_edges() -> None:
    validator = PoseValidator()
    landmarks = _landmarks(
        {
            11: (0.01, 0.3, 0.0, 1.0),
            12: (0.99, 0.3, 0.0, 1.0),
            23: (0.02, 0.45, 0.0, 1.0),
            24: (0.98, 0.45, 0.0, 1.0),
        }
    )

    result = validator.validate(landmarks, 1280, 720)

    assert result.status == ValidationStatus.WARNING
    assert result.message == "Move Back"


def test_pose_validator_reports_stand_straight_for_tilted_pose() -> None:
    validator = PoseValidator()
    landmarks = _landmarks(
        {
            11: (0.45, 0.28, 0.0, 1.0),
            12: (0.55, 0.42, 0.0, 1.0),
            23: (0.46, 0.52, 0.0, 1.0),
            24: (0.54, 0.66, 0.0, 1.0),
        }
    )

    result = validator.validate(landmarks, 1280, 720)

    assert result.status == ValidationStatus.WARNING
    assert result.message == "Stand Straight"


def test_pose_validator_reports_no_person_detected() -> None:
    validator = PoseValidator()

    result = validator.validate(None, 1280, 720)

    assert result.status == ValidationStatus.ERROR
    assert result.message == "No Person Detected"
