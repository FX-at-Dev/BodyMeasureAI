from __future__ import annotations

import time

import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QWidget

from src.ai.pose_detector import PoseDetector
from src.renderers.pose_renderer import PoseRenderer
from src.services.camera_service import CameraService


class CameraWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.camera = CameraService()

        self.frame = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)

        self.pose_detector = PoseDetector()
        
        self.pose_renderer = PoseRenderer()
        
        self.landmarks = None
        
        self.last_time = time.time()
        
        self.fps = 0

    def start(self):

        if self.camera.start():
            self.timer.start(33)

    def stop(self):

        self.timer.stop()
        self.camera.stop()

    def next_frame(self):

        frame = self.camera.get_frame()

        self.landmarks = self.pose_detector.detect(frame)
        
        current = time.time()
        
        self.fps = 1/(current-self.last_time)
        
        self.last_time = current

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

        if self.landmarks:
            self.pose_renderer.draw(
                        painter,
                        self.landmarks,
                        image.width(),
                        image.height(),
                        )
        painter.setPen(QColor("yellow"))
        
        painter.drawText(
            10,
            30,
            f"FPS : {self.fps:.1f}"
        )

    def closeEvent(self, event):

        self.stop()

        super().closeEvent(event)