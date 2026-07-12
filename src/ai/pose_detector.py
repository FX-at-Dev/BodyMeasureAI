from __future__ import annotations

from typing import Any, cast

import cv2
import mediapipe as mp
import numpy as np
from numpy.typing import NDArray

from src.config import AISettings, load_settings

Frame = NDArray[np.uint8]


class PoseDetector:
    """Runs MediaPipe Pose on an image."""

    def __init__(self, settings: AISettings | None = None) -> None:
        """Initialize MediaPipe with configured or explicitly supplied AI settings."""
        ai_settings = settings or load_settings().ai
        self._pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=ai_settings.model_complexity,
            smooth_landmarks=ai_settings.smooth_landmarks,
            enable_segmentation=False,
            min_detection_confidence=ai_settings.min_detection_confidence,
            min_tracking_confidence=ai_settings.min_tracking_confidence,
        )

    def detect(self, frame: Frame) -> list[Any] | None:
        """Return detected landmarks for a BGR camera frame."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = self._pose.process(rgb)

        if result.pose_landmarks is None:
            return None

        return cast(list[Any], result.pose_landmarks.landmark)

    def close(self) -> None:
        self._pose.close()
