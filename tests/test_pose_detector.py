from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

from src.ai import pose_detector
from src.config import AISettings


class FakePose:
    """Controllable MediaPipe Pose replacement."""

    def __init__(self, result: Any) -> None:
        self.result = result
        self.processed_frame: Any | None = None
        self.closed = False

    def process(self, frame: Any) -> Any:
        self.processed_frame = frame
        return self.result

    def close(self) -> None:
        self.closed = True


def test_pose_detector_uses_configured_settings_and_returns_landmarks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    landmarks = [SimpleNamespace(x=0.1, y=0.2)]
    fake_pose = FakePose(
        SimpleNamespace(pose_landmarks=SimpleNamespace(landmark=landmarks))
    )
    pose_arguments: dict[str, Any] = {}
    rgb_frame = object()

    def create_pose(**kwargs: Any) -> FakePose:
        pose_arguments.update(kwargs)
        return fake_pose

    monkeypatch.setattr(pose_detector.mp.solutions.pose, "Pose", create_pose)
    monkeypatch.setattr(pose_detector.cv2, "cvtColor", lambda *_: rgb_frame)
    detector = pose_detector.PoseDetector(
        AISettings(
            model_complexity=2,
            smooth_landmarks=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.8,
        )
    )

    result = detector.detect(np.zeros((2, 2, 3), dtype=np.uint8))
    detector.close()

    assert result == landmarks
    assert fake_pose.processed_frame is rgb_frame
    assert pose_arguments["model_complexity"] == 2
    assert not pose_arguments["smooth_landmarks"]
    assert pose_arguments["min_detection_confidence"] == 0.7
    assert pose_arguments["min_tracking_confidence"] == 0.8
    assert fake_pose.closed


def test_pose_detector_returns_none_when_pose_is_not_detected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_pose = FakePose(SimpleNamespace(pose_landmarks=None))
    monkeypatch.setattr(pose_detector.mp.solutions.pose, "Pose", lambda **_: fake_pose)
    detector = pose_detector.PoseDetector(AISettings())

    assert detector.detect(np.zeros((2, 2, 3), dtype=np.uint8)) is None
