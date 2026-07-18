"""Live-camera page and pose-worker coordinator."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import cv2
from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QHideEvent, QImage, QShowEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.ai.calibration import CalibrationManager, CalibrationResult
from src.ai.measurement_engine import MeasurementEngine
from src.ai.pose_validator import PoseValidator
from src.config import load_settings
from src.models.measurement import Measurement
from src.services.camera_service import CameraService, Frame
from src.ui.widgets.calibration_status_widget import CalibrationStatusWidget
from src.ui.widgets.camera_widget import CameraWidget
from src.workers.pose_worker import PoseWorker
from src.workers.review_measurement_worker import ReviewMeasurementWorker

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
        self._pose_validator = PoseValidator()
        self._calibration_manager = CalibrationManager()
        self._measurement_engine = MeasurementEngine()
        self._review_measurement_worker: ReviewMeasurementWorker | None = None
        self._latest_landmarks: tuple[Any, ...] = ()
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
        self._current_frame_size: tuple[int, int] | None = None

        self._pose_worker.landmarks_ready.connect(self._on_landmarks_ready)
        self._pose_worker.inference_finished.connect(self._on_inference_finished)
        self._pose_worker.inference_failed.connect(self._on_inference_failed)
        self._pose_worker.finished.connect(self._on_worker_finished)

        self.status = QLabel("Camera ready")
        self.calibration_status = CalibrationStatusWidget(self)
        self.calibration_status.set_calibration(
            self._calibration_manager.calibration_data
        )
        self.capture_button = QPushButton("📸 Capture")
        self.capture_button.clicked.connect(self._review_height)
        self.import_button = QPushButton("📂 Import")
        self.reference_calibration_button = QPushButton("Calibrate Reference")
        self.height_calibration_button = QPushButton("Calibrate Known Height")
        self.reference_calibration_button.clicked.connect(
            self._calibrate_reference_object
        )
        self.height_calibration_button.clicked.connect(self._calibrate_known_height)
        self.back_button = QPushButton("⬅ Back")
        self.back_button.clicked.connect(self.main_window.go_home)

        buttons = QHBoxLayout()
        buttons.addWidget(self.import_button)
        buttons.addWidget(self.capture_button)
        buttons.addWidget(self.reference_calibration_button)
        buttons.addWidget(self.height_calibration_button)
        buttons.addStretch()
        buttons.addWidget(self.back_button)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.calibration_status)
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
        self.preview.clear_validation_result()
        self._current_frame_size = None

    def _next_frame(self) -> None:
        frame = self._camera_service.get_frame()

        if frame is None:
            self.status.setText("Camera frame unavailable")
            return

        height, width = frame.shape[:2]
        self._current_frame_size = (width, height)
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
            self._latest_landmarks = tuple(landmarks or ())
            self.preview.set_landmarks(landmarks)
            if self._current_frame_size is not None:
                width, height = self._current_frame_size
                self.preview.set_validation_result(
                    self._pose_validator.validate(landmarks, width, height)
                )

    def _on_inference_finished(self, frame_id: int) -> None:
        if frame_id == self._frame_id:
            self._inference_pending = False

    def _on_inference_failed(self, _message: str, frame_id: int) -> None:
        if frame_id == self._frame_id:
            self.preview.clear_landmarks()
            self.preview.clear_validation_result()
            self.status.setText("Pose detection unavailable")

    def _on_worker_finished(self) -> None:
        if self._shutdown_requested:
            self.shutdown_finished.emit()

    def _review_height(self) -> None:
        """Calculate the latest pose height in a worker before opening review."""
        if (
            self._review_measurement_worker is not None
            and self._review_measurement_worker.isRunning()
        ):
            return
        if self._current_frame_size is None:
            self.status.setText("Camera frame unavailable")
            return

        image_width, image_height = self._current_frame_size
        self._review_measurement_worker = ReviewMeasurementWorker(
            landmarks=self._latest_landmarks,
            image_width_pixels=image_width,
            image_height_pixels=image_height,
            calibration=self._calibration_manager.calibration_data,
            measurement_engine=self._measurement_engine,
            parent=self,
        )
        self._review_measurement_worker.measurements_ready.connect(
            self._show_measurement_review
        )
        self._review_measurement_worker.measurement_failed.connect(
            self._on_height_measurement_failed
        )
        self._review_measurement_worker.start()

    def _show_height_review(self, measurement: object) -> None:
        self.main_window.show_height_review(cast("Measurement", measurement))
        self._review_measurement_worker = None

    def _show_measurement_review(self, measurements: object) -> None:
        self.main_window.show_measurement_review(
            cast("tuple[Measurement, ...]", measurements)
        )
        self._review_measurement_worker = None

    def _on_height_measurement_failed(self, message: str) -> None:
        self.status.setText(f"Height measurement unavailable: {message}")
        self._review_measurement_worker = None

    def _calibrate_reference_object(self) -> None:
        reference_name, accepted = QInputDialog.getText(
            self,
            "Reference-object calibration",
            "Reference name:",
        )
        if not accepted:
            return
        known_length_cm = self._get_positive_value("Known reference length (cm):")
        if known_length_cm is None:
            return
        measured_pixels = self._get_positive_value(
            "Measured reference length (pixels):"
        )
        if measured_pixels is None:
            return
        self._apply_calibration_result(
            self._calibration_manager.recalibrate_reference_object(
                reference_name,
                known_length_cm,
                measured_pixels,
            )
        )

    def _calibrate_known_height(self) -> None:
        known_height_cm = self._get_positive_value("Known person height (cm):")
        if known_height_cm is None:
            return
        measured_pixels = self._get_positive_value("Visible person height (pixels):")
        if measured_pixels is None:
            return
        self._apply_calibration_result(
            self._calibration_manager.recalibrate_known_height(
                known_height_cm,
                measured_pixels,
            )
        )

    def _apply_calibration_result(self, result: CalibrationResult) -> None:
        if result.is_calibrated:
            self.calibration_status.set_calibration(result.calibration_data)
            self.status.setText("Calibration saved locally")
            return

        QMessageBox.warning(self, "Calibration unavailable", result.error_message or "")

    def _get_positive_value(self, label: str) -> float | None:
        value, accepted = QInputDialog.getDouble(
            self,
            "Calibration",
            label,
            minValue=0.01,
            maxValue=1_000_000.0,
            decimals=2,
        )
        return value if accepted else None

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
