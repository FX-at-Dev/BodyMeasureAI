"""Pose-validation heuristics for live camera framing."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from src.models.validation_result import ValidationResult, ValidationStatus


@dataclass(frozen=True)
class PoseValidator:
    """Validate a detected pose before the measurement workflow proceeds."""

    minimum_visibility: float = 0.6
    edge_margin: float = 0.05
    straightness_threshold: float = 0.08

    _HEAD_INDICES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    _LEFT_SHOULDER = 11
    _RIGHT_SHOULDER = 12
    _LEFT_HIP = 23
    _RIGHT_HIP = 24
    _LEFT_KNEE = 25
    _RIGHT_KNEE = 26
    _LEFT_FOOT = (27, 29, 31)
    _RIGHT_FOOT = (28, 30, 32)

    def validate(
        self,
        landmarks: Sequence[Any] | None,
        frame_width: int,
        frame_height: int,
    ) -> ValidationResult:
        """Return a validation result for the supplied pose landmarks."""
        _ = frame_width, frame_height

        if not landmarks:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message="No Person Detected",
                issues=("no_person_detected",),
            )

        if not self._group_visible(landmarks, self._HEAD_INDICES):
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="Move Back",
                issues=("head_not_visible",),
            )

        if not self._landmark_visible(landmarks, self._LEFT_SHOULDER):
            return self._missing_body_part("shoulders_not_visible")

        if not self._landmark_visible(landmarks, self._RIGHT_SHOULDER):
            return self._missing_body_part("shoulders_not_visible")

        if not self._landmark_visible(landmarks, self._LEFT_HIP):
            return self._missing_body_part("hips_not_visible")

        if not self._landmark_visible(landmarks, self._RIGHT_HIP):
            return self._missing_body_part("hips_not_visible")

        if not self._landmark_visible(landmarks, self._LEFT_KNEE):
            return self._missing_body_part("knees_not_visible")

        if not self._landmark_visible(landmarks, self._RIGHT_KNEE):
            return self._missing_body_part("knees_not_visible")

        if not self._foot_visible(landmarks, self._LEFT_FOOT):
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="Feet Not Visible",
                issues=("left_foot_not_visible",),
            )

        if not self._foot_visible(landmarks, self._RIGHT_FOOT):
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="Feet Not Visible",
                issues=("right_foot_not_visible",),
            )

        if not self._body_inside_frame(landmarks):
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message="Entire Body Not Visible",
                issues=("body_outside_frame",),
            )

        if self._body_too_close_to_frame_edges(landmarks):
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="Move Back",
                issues=("body_too_close_to_frame_edges",),
            )

        if not self._stands_straight(landmarks):
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="Stand Straight",
                issues=("body_not_straight",),
            )

        return ValidationResult(
            status=ValidationStatus.READY,
            message="Ready",
        )

    def _missing_body_part(self, issue: str) -> ValidationResult:
        return ValidationResult(
            status=ValidationStatus.ERROR,
            message="Entire Body Not Visible",
            issues=(issue,),
        )

    def _landmark_visible(self, landmarks: Sequence[Any], index: int) -> bool:
        landmark = self._landmark(landmarks, index)
        return self._is_visible(landmark)

    def _group_visible(self, landmarks: Sequence[Any], indices: Sequence[int]) -> bool:
        return any(self._landmark_visible(landmarks, index) for index in indices)

    def _foot_visible(self, landmarks: Sequence[Any], indices: Sequence[int]) -> bool:
        return any(self._landmark_visible(landmarks, index) for index in indices)

    def _body_inside_frame(self, landmarks: Sequence[Any]) -> bool:
        for index in self._tracked_indices():
            landmark = self._landmark(landmarks, index)
            if landmark is None:
                continue

            x = float(getattr(landmark, "x", 0.0))
            y = float(getattr(landmark, "y", 0.0))
            if x < 0.0 or x > 1.0 or y < 0.0 or y > 1.0:
                return False

        return True

    def _body_too_close_to_frame_edges(self, landmarks: Sequence[Any]) -> bool:
        visible_points = [
            self._landmark(landmarks, index) for index in self._tracked_indices()
        ]
        visible_points = [point for point in visible_points if self._is_visible(point)]

        if not visible_points:
            return False

        min_x = min(float(getattr(point, "x", 0.0)) for point in visible_points)
        max_x = max(float(getattr(point, "x", 0.0)) for point in visible_points)
        min_y = min(float(getattr(point, "y", 0.0)) for point in visible_points)
        max_y = max(float(getattr(point, "y", 0.0)) for point in visible_points)
        margin = self.edge_margin

        return (
            min_x < margin
            or max_x > 1.0 - margin
            or min_y < margin
            or max_y > 1.0 - margin
        )

    def _stands_straight(self, landmarks: Sequence[Any]) -> bool:
        left_shoulder = self._landmark(landmarks, self._LEFT_SHOULDER)
        right_shoulder = self._landmark(landmarks, self._RIGHT_SHOULDER)
        left_hip = self._landmark(landmarks, self._LEFT_HIP)
        right_hip = self._landmark(landmarks, self._RIGHT_HIP)

        if (
            left_shoulder is None
            or right_shoulder is None
            or left_hip is None
            or right_hip is None
        ):
            return False

        if not all(
            self._is_visible(point)
            for point in (left_shoulder, right_shoulder, left_hip, right_hip)
        ):
            return False

        shoulder_offset = abs(float(left_shoulder.y) - float(right_shoulder.y))
        hip_offset = abs(float(left_hip.y) - float(right_hip.y))
        return (
            shoulder_offset <= self.straightness_threshold
            and hip_offset <= self.straightness_threshold
        )

    @staticmethod
    def _tracked_indices() -> tuple[int, ...]:
        return (
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
        )

    @staticmethod
    def _landmark(landmarks: Sequence[Any], index: int) -> Any | None:
        if index >= len(landmarks):
            return None
        return landmarks[index]

    def _is_visible(self, landmark: Any | None) -> bool:
        if landmark is None:
            return False

        visibility = float(getattr(landmark, "visibility", 1.0))
        return visibility >= self.minimum_visibility
