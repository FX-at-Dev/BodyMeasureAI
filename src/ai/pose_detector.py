from __future__ import annotations

from typing import Any, cast

import cv2
import mediapipe as mp


class PoseDetector:
    """Runs MediaPipe Pose on an image."""

    def __init__(self) -> None:
        self._pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def detect(self, frame) -> list[Any] | None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = self._pose.process(rgb)

        if result.pose_landmarks is None:
            return None

        return cast(list[Any], result.pose_landmarks.landmark)

    def close(self) -> None:
        self._pose.close()
