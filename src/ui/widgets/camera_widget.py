from __future__ import annotations

import cv2

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel

from src.services.camera_service import CameraService


class CameraWidget(QLabel):
    """Displays a live webcam feed."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAlignment(Qt.AlignCenter)
        self.setText("Starting camera...")

        self.camera = CameraService()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def start(self):

        if self.camera.start():
            self.timer.start(33)
        else:
            self.setText("Unable to open camera")

    def stop(self):

        self.timer.stop()
        self.camera.stop()

    def update_frame(self):

        frame = self.camera.get_frame()

        if frame is None:
            return

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        h, w, ch = frame.shape

        image = QImage(
            frame.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888,
        )

        pixmap = QPixmap.fromImage(image)

        self.setPixmap(
            pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def resizeEvent(self, event):

        if self.pixmap():
            self.setPixmap(
                self.pixmap().scaled(
                    self.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

        super().resizeEvent(event)

    def closeEvent(self, event):

        self.stop()

        super().closeEvent(event)