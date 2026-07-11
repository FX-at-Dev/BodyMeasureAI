from __future__ import annotations

import cv2

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QWidget

from src.services.camera_service import CameraService


class CameraWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.camera = CameraService()

        self.frame = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)

    def start(self):

        if self.camera.start():
            self.timer.start(33)

    def stop(self):

        self.timer.stop()
        self.camera.stop()

    def next_frame(self):

        frame = self.camera.get_frame()

        if frame is None:
            return

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        h, w, c = frame.shape

        self.frame = QImage(
            frame.data,
            w,
            h,
            c * w,
            QImage.Format.Format_RGB888,
        ).copy()

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.fillRect(self.rect(), Qt.black)

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

    def closeEvent(self, event):

        self.stop()

        super().closeEvent(event)