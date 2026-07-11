from __future__ import annotations

import cv2
import mediapipe as mp


class PoseDetector:

    def __init__(self):

        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def detect(self, frame):

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        result = self.pose.process(rgb)

        if result.pose_landmarks:
            return result.pose_landmarks.landmark

        return None