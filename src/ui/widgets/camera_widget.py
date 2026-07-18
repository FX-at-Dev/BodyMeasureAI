"""Camera-preview widget with optional pose overlay rendering."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QElapsedTimer, QRect, Qt, Slot
from PySide6.QtGui import QColor, QImage, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget

from src.models.validation_result import ValidationResult, ValidationStatus
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
        self._validation_result: ValidationResult | None = None
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

    @Slot(object)
    def set_validation_result(self, validation_result: ValidationResult | None) -> None:
        """Display the latest pose-validation message."""
        self._validation_result = validation_result
        self.update()

    def clear_validation_result(self) -> None:
        """Remove the currently displayed pose-validation message."""
        self.set_validation_result(None)

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

            self._draw_validation_banner(painter)
            painter.setPen(QColor("yellow"))
            painter.drawText(10, 30, f"FPS: {self._fps:.1f}")
        finally:
            painter.end()

    def _draw_validation_banner(self, painter: QPainter) -> None:
        if self._validation_result is None:
            return

        text = self._validation_text(self._validation_result)
        metrics = painter.fontMetrics()
        text_rect = metrics.boundingRect(text)
        padding_x = 12
        padding_y = 8
        banner_rect = QRect(
            10,
            self.height() - text_rect.height() - (padding_y * 2) - 12,
            text_rect.width() + (padding_x * 2),
            text_rect.height() + (padding_y * 2),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.drawRoundedRect(banner_rect, 8, 8)
        painter.setPen(self._validation_color(self._validation_result))
        painter.drawText(banner_rect, Qt.AlignmentFlag.AlignCenter, text)

    @staticmethod
    def _validation_text(validation_result: ValidationResult) -> str:
        prefix = "✓" if validation_result.status == ValidationStatus.READY else "⚠"
        return f"{prefix} {validation_result.message}"

    @staticmethod
    def _validation_color(validation_result: ValidationResult) -> QColor:
        if validation_result.status == ValidationStatus.READY:
            return QColor("#8DEB8D")

        return QColor("#FFCB6B")
