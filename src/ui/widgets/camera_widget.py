from __future__ import annotations

import time
from typing import Any

import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QColor, QImage, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget

from src.ai.pose_detector import PoseDetector
from src.renderers.pose_renderer import PoseRenderer
from src.services.camera_service import CameraService


class CameraWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.camera = CameraService()

        self.frame: QImage | None = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)

        self.pose_detector = PoseDetector()

        self.pose_renderer = PoseRenderer()

        self.landmarks: list[Any] | None = None

        self.last_time = time.time()

        self.fps: float = 0.0

    def start(self):

        if self.camera.start():
            self.timer.start(33)

    def stop(self) -> None:
        self.timer.stop()

        self.camera.stop()

        self.pose_detector.close()

    def next_frame(self) -> None:
        frame = self.camera.get_frame()

        if frame is None:
            print("NO FRAME")
            return
        print(frame.shape)

        # self.landmarks = self.pose_detector.detect(frame)
        # TEMPORARILY DISABLE AI
        self.landmarks = None

        current = time.time()
        delta = current - self.last_time

        if delta > 0:
            self.fps = 1.0 / delta

        self.last_time = current

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, c = frame.shape

        self.frame = QImage(
            frame.data,
            w,
            h,
            c * w,
            QImage.Format.Format_RGB888,
        ).copy()

        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        _ = event

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        painter.fillRect(
            self.rect(),
            QColor("black"),
        )

        if self.frame is None:
            return

        image = self.frame.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        x = (self.width() - image.width()) // 2
        y = (self.height() - image.height()) // 2

        painter.drawImage(x, y, image)

        image_width = image.width()
        image_height = image.height()

        image_x = (self.width() - image_width) // 2
        image_y = (self.height() - image_height) // 2

        if self.landmarks is not None:
            self.pose_renderer.draw(
                painter,
                self.landmarks,
                image_x,
                image_y,
                image_width,
                image_height,
            )

        painter.setPen(QColor("yellow"))

        painter.drawText(10, 30, f"FPS : {self.fps:.1f}")

    def closeEvent(self, event: QCloseEvent) -> None:

        self.stop()

        super().closeEvent(event)
