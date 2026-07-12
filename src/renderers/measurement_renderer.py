"""Rendering primitives for future body-measurement overlays."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen


@dataclass(frozen=True)
class MeasurementOverlay:
    """A labeled line expressed in normalized camera-image coordinates."""

    label: str
    start: tuple[float, float]
    end: tuple[float, float]
    color: str = "#4FC3F7"


class MeasurementRenderer:
    """Draw measurement overlay data supplied by future measurement logic."""

    def draw(
        self,
        painter: QPainter,
        overlays: Sequence[MeasurementOverlay],
        image_x: int,
        image_y: int,
        image_width: int,
        image_height: int,
    ) -> None:
        """Draw normalized measurement lines and their labels."""
        for overlay in overlays:
            start = self._to_image_point(
                overlay.start,
                image_x,
                image_y,
                image_width,
                image_height,
            )
            end = self._to_image_point(
                overlay.end,
                image_x,
                image_y,
                image_width,
                image_height,
            )
            color = QColor(overlay.color)
            pen = QPen(color, 2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(start, end)

            midpoint = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)
            painter.drawText(midpoint, overlay.label)

    @staticmethod
    def _to_image_point(
        point: tuple[float, float],
        image_x: int,
        image_y: int,
        image_width: int,
        image_height: int,
    ) -> QPointF:
        return QPointF(
            image_x + point[0] * image_width,
            image_y + point[1] * image_height,
        )
