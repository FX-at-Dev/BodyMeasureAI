"""Threaded MediaPipe pose-inference worker."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import QMutex, QObject, QThread, QWaitCondition, Signal

from src.ai.pose_detector import PoseDetector

Frame = NDArray[np.uint8]


class PoseDetectorProtocol(Protocol):
    """The detector interface required by :class:`PoseWorker`."""

    def detect(self, frame: Frame) -> list[Any] | None:
        """Detect pose landmarks in a BGR image."""

    def close(self) -> None:
        """Release detector resources."""


class PoseWorker(QThread):
    """Run pose inference off the Qt GUI thread.

    Only the newest submitted frame is retained.  The widget intentionally
    submits at most one frame at a time, while this safeguard also prevents a
    growing backlog if a caller submits frames faster than inference completes.
    """

    landmarks_ready = Signal(object, int)
    inference_failed = Signal(str, int)
    inference_finished = Signal(int)

    def __init__(
        self,
        detector_factory: Callable[[], PoseDetectorProtocol] = PoseDetector,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._detector_factory = detector_factory
        self._mutex = QMutex()
        self._frame_available = QWaitCondition()
        self._pending_frame: Frame | None = None
        self._pending_frame_id = 0

    def submit_frame(self, frame: Frame, frame_id: int) -> None:
        """Queue a frame for inference without blocking the caller."""
        frame_copy = frame.copy()

        self._mutex.lock()
        try:
            self._pending_frame = frame_copy
            self._pending_frame_id = frame_id
            self._frame_available.wakeOne()
        finally:
            self._mutex.unlock()

    def stop(self) -> None:
        """Request that the worker exits after its current inference call."""
        self.requestInterruption()

        self._mutex.lock()
        try:
            self._frame_available.wakeAll()
        finally:
            self._mutex.unlock()

    def run(self) -> None:
        """Create and use MediaPipe only from this worker thread."""
        detector: PoseDetectorProtocol | None = None

        try:
            detector = self._detector_factory()
            self._process_frames(detector)
        except Exception as error:
            self.inference_failed.emit(str(error), 0)
        finally:
            if detector is not None:
                detector.close()

    def _process_frames(self, detector: PoseDetectorProtocol) -> None:
        while not self.isInterruptionRequested():
            frame, frame_id = self._take_pending_frame()

            if frame is None:
                continue

            try:
                landmarks = detector.detect(frame)
                self.landmarks_ready.emit(landmarks, frame_id)
            except Exception as error:
                self.inference_failed.emit(str(error), frame_id)
            finally:
                self.inference_finished.emit(frame_id)

    def _take_pending_frame(self) -> tuple[Frame | None, int]:
        self._mutex.lock()
        try:
            while self._pending_frame is None and not self.isInterruptionRequested():
                self._frame_available.wait(self._mutex)

            frame = self._pending_frame
            frame_id = self._pending_frame_id
            self._pending_frame = None
            return frame, frame_id
        finally:
            self._mutex.unlock()
