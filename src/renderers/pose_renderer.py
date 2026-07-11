from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPen


class PoseRenderer:
    """Draws MediaPipe pose landmarks."""

    CONNECTIONS = [
        (11, 13),
        (13, 15),
        (12, 14),
        (14, 16),
        (11, 12),
        (11, 23),
        (12, 24),
        (23, 24),
        (23, 25),
        (25, 27),
        (24, 26),
        (26, 28),
        (27, 31),
        (28, 32),
    ]

    def draw(
        self,
        painter: QPainter,
        landmarks: list[Any] | None,
        image_x: int,
        image_y: int,
        image_width: int,
        image_height: int,
    ) -> None:

        if landmarks is None:
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor("#00FF88"))
        pen.setWidth(3)

        painter.setPen(pen)
        painter.setBrush(QColor("#FF5555"))

        # Draw bones
        for start, end in self.CONNECTIONS:
            a = landmarks[start]
            b = landmarks[end]

            painter.drawLine(
                QPointF(
                    image_x + a.x * image_width,
                    image_y + a.y * image_height,
                ),
                QPointF(
                    image_x + b.x * image_width,
                    image_y + b.y * image_height,
                ),
            )

        # Draw joints
        for lm in landmarks:
            painter.drawEllipse(
                QPointF(
                    image_x + lm.x * image_width,
                    image_y + lm.y * image_height,
                ),
                4,
                4,
            )
