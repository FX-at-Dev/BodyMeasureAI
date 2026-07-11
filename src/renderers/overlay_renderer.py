from __future__ import annotations

from src.renderers.pose_renderer import PoseRenderer


class OverlayRenderer:

    def __init__(self):

        self.pose = PoseRenderer()

    def draw(
        self,
        painter,
        pose_landmarks,
        width,
        height,
    ):

        self.pose.draw(
            painter,
            pose_landmarks,
            width,
            height,
        )