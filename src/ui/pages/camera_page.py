"""Live-camera page and pose-worker coordinator."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import cv2
from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QHideEvent, QImage, QShowEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.config import load_settings
from src.services.camera_service import CameraService, Frame
from src.ui.widgets.camera_widget import CameraWidget
from src.workers.pose_worker import PoseWorker

if TYPE_CHECKING:
    from src.ui.windows.main_window import MainWindow


class CameraPage(QWidget):
    """Coordinate camera capture and worker inference for the camera preview."""

    shutdown_finished = Signal()

    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.main_window = window
        settings = load_settings()
        self.preview = CameraWidget(
            self,
            show_landmark_ids=settings.ui.show_landmark_ids,
        )
        self._camera_service = CameraService(
            camera_index=settings.camera.index,
            resolution=(settings.camera.width, settings.camera.height),
            fps=settings.camera.fps,
        )
        self._pose_worker = PoseWorker(parent=self)
        self._frame_timer = QTimer(self)
        self._frame_timer.timeout.connect(self._next_frame)
        self._frame_id = 0
        self._inference_pending = False
        self._shutdown_requested = False

        self._pose_worker.landmarks_ready.connect(self._on_landmarks_ready)
        self._pose_worker.inference_finished.connect(self._on_inference_finished)
        self._pose_worker.inference_failed.connect(self._on_inference_failed)
        self._pose_worker.finished.connect(self._on_worker_finished)

        self.status = QLabel("Camera ready")
        self.capture_button = QPushButton("📸 Capture")
        self.import_button = QPushButton("📂 Import")
        self.back_button = QPushButton("⬅ Back")
        self.back_button.clicked.connect(self.main_window.go_home)

        buttons = QHBoxLayout()
        buttons.addWidget(self.import_button)
        buttons.addWidget(self.capture_button)
        buttons.addStretch()
        buttons.addWidget(self.back_button)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        self.preview.setMinimumSize(800, 600)
        layout.addWidget(self.preview)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def showEvent(self, event: QShowEvent) -> None:
        """Start live capture when the page becomes visible."""
        self._start_camera()
        super().showEvent(event)

    def hideEvent(self, event: QHideEvent) -> None:
        """Release the camera when the page is hidden."""
        self._stop_camera()
        super().hideEvent(event)

    def shutdown(self) -> bool:
        """Stop all camera resources without waiting on the GUI thread.

        Returns ``True`` once the worker has stopped and the page may be
        destroyed.  Otherwise, ``shutdown_finished`` is emitted asynchronously.
        """
        self._stop_camera()
        self._shutdown_requested = True

        if not self._pose_worker.isRunning():
            return True

        self._pose_worker.stop()
        return False

    def _start_camera(self) -> None:
        if not self._camera_service.start():
            self.status.setText("Camera unavailable")
            return

        if not self._pose_worker.isRunning():
            self._pose_worker.start()

        self.status.setText("Camera active")
        self._frame_timer.start(33)

    def _stop_camera(self) -> None:
        self._frame_timer.stop()
        self._camera_service.stop()
        self._frame_id += 1
        self._inference_pending = False
        self.preview.clear_landmarks()

    def _next_frame(self) -> None:
        frame = self._camera_service.get_frame()

        if frame is None:
            self.status.setText("Camera frame unavailable")
            return

        self._submit_for_inference(frame)
        self.preview.display_frame(self._to_qimage(frame))

    def _submit_for_inference(self, frame: Frame) -> None:
        if not self._pose_worker.isRunning() or self._inference_pending:
            return

        self._inference_pending = True
        self._frame_id += 1
        self._pose_worker.submit_frame(frame, self._frame_id)

    def _on_landmarks_ready(
        self,
        landmarks: list[Any] | None,
        frame_id: int,
    ) -> None:
        if frame_id == self._frame_id:
            self.preview.set_landmarks(landmarks)

    def _on_inference_finished(self, frame_id: int) -> None:
        if frame_id == self._frame_id:
            self._inference_pending = False

    def _on_inference_failed(self, _message: str, frame_id: int) -> None:
        if frame_id == self._frame_id:
            self.preview.clear_landmarks()
            self.status.setText("Pose detection unavailable")

    def _on_worker_finished(self) -> None:
        if self._shutdown_requested:
            self.shutdown_finished.emit()

    @staticmethod
    def _to_qimage(frame: Frame) -> QImage:
        rgb_frame = cast(Frame, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        height, width, channels = rgb_frame.shape
        return QImage(
            rgb_frame.data,
            width,
            height,
            channels * width,
            QImage.Format.Format_RGB888,
        ).copy()
