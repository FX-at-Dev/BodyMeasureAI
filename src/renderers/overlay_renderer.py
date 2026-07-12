from __future__ import annotations

from typing import Any

from PySide6.QtGui import QPainter

from src.renderers.pose_renderer import PoseRenderer


class OverlayRenderer:
    """Draw pose overlays over a camera image."""

    def __init__(self) -> None:
        self.pose = PoseRenderer()

    def draw(
        self,
        painter: QPainter,
        pose_landmarks: list[Any] | None,
        width: int,
        height: int,
    ) -> None:
        """Draw pose landmarks across the supplied image dimensions."""
        self.pose.draw(
            painter,
            pose_landmarks,
            0,
            0,
            width,
            height,
        )
