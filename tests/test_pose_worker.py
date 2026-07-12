from __future__ import annotations

import time

import numpy as np
from PySide6.QtCore import QCoreApplication

from src.workers.pose_worker import Frame, PoseWorker


class FakePoseDetector:
    """Deterministic detector used to test the worker lifecycle."""

    def __init__(self) -> None:
        self.closed = False

    def detect(self, frame: Frame) -> list[str]:
        _ = frame
        return ["pose"]

    def close(self) -> None:
        self.closed = True


class FailingPoseDetector(FakePoseDetector):
    """Detector double that reports an inference error."""

    def detect(self, frame: Frame) -> list[str]:
        _ = frame
        raise RuntimeError("inference failed")


def test_pose_worker_emits_landmarks_and_closes_detector() -> None:
    app = QCoreApplication.instance() or QCoreApplication([])
    detector = FakePoseDetector()
    worker = PoseWorker(detector_factory=lambda: detector)
    received: list[tuple[list[str], int]] = []
    worker.landmarks_ready.connect(
        lambda landmarks, frame_id: received.append((landmarks, frame_id))
    )

    worker.start()
    worker.submit_frame(np.zeros((4, 4, 3), dtype=np.uint8), 7)

    deadline = time.monotonic() + 1.0
    while not received and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)

    worker.stop()
    assert worker.wait(1000)
    assert received == [(["pose"], 7)]
    assert detector.closed


def test_pose_worker_emits_inference_failures_and_stops_cleanly() -> None:
    app = QCoreApplication.instance() or QCoreApplication([])
    detector = FailingPoseDetector()
    worker = PoseWorker(detector_factory=lambda: detector)
    failures: list[tuple[str, int]] = []
    worker.inference_failed.connect(
        lambda message, frame_id: failures.append((message, frame_id))
    )

    worker.start()
    worker.submit_frame(np.zeros((4, 4, 3), dtype=np.uint8), 9)

    deadline = time.monotonic() + 1.0
    while not failures and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)

    worker.stop()
    assert worker.wait(1000)
    assert failures == [("inference failed", 9)]
    assert detector.closed
