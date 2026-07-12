"""Camera-preview widget with optional pose overlay rendering."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QElapsedTimer, QRect, Qt, Slot
from PySide6.QtGui import QColor, QImage, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget

from src.renderers.pose_renderer import PoseRenderer


class CameraWidget(QWidget):
    """Display supplied camera frames and pose landmarks without inference."""

    def __init__(
        self,
        parent: QWidget | None = None,
        show_landmark_ids: bool = False,
    ) -> None:
        super().__init__(parent)
        self._frame: QImage | None = None
        self._landmarks: list[Any] | None = None
        self._pose_renderer = PoseRenderer(show_landmark_ids=show_landmark_ids)
        self._frame_timer = QElapsedTimer()
        self._frame_timer.start()
        self._last_frame_time_ms: int | None = None
        self._fps = 0.0

    @Slot(QImage)
    def display_frame(self, frame: QImage) -> None:
        """Display an already converted frame and update preview FPS."""
        self._frame = frame
        self._update_fps()
        self.update()

    @Slot(object)
    def set_landmarks(self, landmarks: list[Any] | None) -> None:
        """Display pose landmarks received from the pose worker."""
        self._landmarks = landmarks
        self.update()

    def clear_landmarks(self) -> None:
        """Remove the currently displayed pose overlay."""
        self.set_landmarks(None)

    def _update_fps(self) -> None:
        current_time_ms = self._frame_timer.elapsed()

        if self._last_frame_time_ms is not None:
            elapsed_ms = current_time_ms - self._last_frame_time_ms
            if elapsed_ms > 0:
                self._fps = 1000.0 / elapsed_ms

        self._last_frame_time_ms = current_time_ms

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draw the camera frame and landmarks without creating scaled images."""
        _ = event
        painter = QPainter(self)

        try:
            painter.fillRect(self.rect(), QColor("black"))

            if self._frame is None:
                return

            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            image_size = self._frame.size()
            image_size.scale(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
            image_rect = QRect(
                (self.width() - image_size.width()) // 2,
                (self.height() - image_size.height()) // 2,
                image_size.width(),
                image_size.height(),
            )
            painter.drawImage(image_rect, self._frame)

            self._pose_renderer.draw(
                painter,
                self._landmarks,
                image_rect.x(),
                image_rect.y(),
                image_rect.width(),
                image_rect.height(),
            )

            painter.setPen(QColor("yellow"))
            painter.drawText(10, 30, f"FPS: {self._fps:.1f}")
        finally:
            painter.end()
