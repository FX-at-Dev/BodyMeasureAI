"""Custom Qt rendering for pose landmarks and skeleton overlays."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen

from src.renderers.measurement_renderer import MeasurementOverlay, MeasurementRenderer


class PoseRenderer:
    """Draw an antialiased pose skeleton without MediaPipe drawing utilities."""

    CONNECTIONS: list[tuple[int, int]] = [
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
    _SKELETON_COLOR = QColor("#00D084")
    _JOINT_OUTLINE_COLOR = QColor("#101820")

    def __init__(
        self,
        show_landmark_ids: bool = False,
        measurement_renderer: MeasurementRenderer | None = None,
    ) -> None:
        self._show_landmark_ids = show_landmark_ids
        self._measurement_renderer = measurement_renderer or MeasurementRenderer()

    def draw(
        self,
        painter: QPainter,
        landmarks: Sequence[Any] | None,
        image_x: int,
        image_y: int,
        image_width: int,
        image_height: int,
        measurement_overlays: Sequence[MeasurementOverlay] | None = None,
        show_landmark_ids: bool | None = None,
    ) -> None:
        """Draw pose landmarks, optional IDs, and future measurement overlays."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if landmarks is not None:
            self._draw_connections(
                painter,
                landmarks,
                image_x,
                image_y,
                image_width,
                image_height,
            )
            self._draw_joints(
                painter,
                landmarks,
                image_x,
                image_y,
                image_width,
                image_height,
            )

            if self._should_show_landmark_ids(show_landmark_ids):
                self._draw_landmark_ids(
                    painter,
                    landmarks,
                    image_x,
                    image_y,
                    image_width,
                    image_height,
                )

        if measurement_overlays:
            self._measurement_renderer.draw(
                painter,
                measurement_overlays,
                image_x,
                image_y,
                image_width,
                image_height,
            )

    def _draw_connections(
        self,
        painter: QPainter,
        landmarks: Sequence[Any],
        image_x: int,
        image_y: int,
        image_width: int,
        image_height: int,
    ) -> None:
        pen = QPen(self._SKELETON_COLOR, 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        for start_index, end_index in self.CONNECTIONS:
            if start_index >= len(landmarks) or end_index >= len(landmarks):
                continue

            painter.drawLine(
                self._to_image_point(
                    landmarks[start_index],
                    image_x,
                    image_y,
                    image_width,
                    image_height,
                ),
                self._to_image_point(
                    landmarks[end_index],
                    image_x,
                    image_y,
                    image_width,
                    image_height,
                ),
            )

    def _draw_joints(
        self,
        painter: QPainter,
        landmarks: Sequence[Any],
        image_x: int,
        image_y: int,
        image_width: int,
        image_height: int,
    ) -> None:
        outline_pen = QPen(self._JOINT_OUTLINE_COLOR, 1)

        for landmark in landmarks:
            painter.setPen(outline_pen)
            painter.setBrush(self._confidence_color(landmark))
            painter.drawEllipse(
                self._to_image_point(
                    landmark,
                    image_x,
                    image_y,
                    image_width,
                    image_height,
                ),
                4,
                4,
            )

    def _draw_landmark_ids(
        self,
        painter: QPainter,
        landmarks: Sequence[Any],
        image_x: int,
        image_y: int,
        image_width: int,
        image_height: int,
    ) -> None:
        painter.setPen(QColor("white"))

        for landmark_id, landmark in enumerate(landmarks):
            point = self._to_image_point(
                landmark,
                image_x,
                image_y,
                image_width,
                image_height,
            )
            painter.drawText(point + QPointF(6, -6), str(landmark_id))

    def _should_show_landmark_ids(self, show_landmark_ids: bool | None) -> bool:
        return (
            self._show_landmark_ids if show_landmark_ids is None else show_landmark_ids
        )

    @staticmethod
    def _to_image_point(
        landmark: Any,
        image_x: int,
        image_y: int,
        image_width: int,
        image_height: int,
    ) -> QPointF:
        return QPointF(
            image_x + landmark.x * image_width,
            image_y + landmark.y * image_height,
        )

    @staticmethod
    def _confidence_color(landmark: Any) -> QColor:
        confidence = max(0.0, min(1.0, float(getattr(landmark, "visibility", 1.0))))
        return QColor.fromRgb(
            int((1.0 - confidence) * 255),
            int(confidence * 220),
            64,
        )
