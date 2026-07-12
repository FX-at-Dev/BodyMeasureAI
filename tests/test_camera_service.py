from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from src.services.camera_service import CameraService


class FakeCapture:
    """Minimal OpenCV capture double for camera-service tests."""

    def __init__(self, reads: list[tuple[bool, Any]] | None = None) -> None:
        self.opened = True
        self.properties: dict[int, float] = {}
        self.reads = reads or []
        self.released = False

    def isOpened(self) -> bool:
        return self.opened

    def release(self) -> None:
        self.released = True
        self.opened = False

    def set(self, property_id: int, value: float) -> bool:
        self.properties[property_id] = value
        return True

    def read(self) -> tuple[bool, Any]:
        return self.reads.pop(0) if self.reads else (False, None)


def test_camera_creation() -> None:
    assert CameraService() is not None


def test_camera_applies_selected_resolution_and_fps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture = FakeCapture()
    monkeypatch.setattr(
        "src.services.camera_service.cv2.VideoCapture", lambda _: capture
    )
    camera = CameraService(camera_index=2, resolution=(1280, 720), fps=30.0)

    assert camera.start()
    assert camera.camera_index == 2
    assert capture.properties[3] == 1280
    assert capture.properties[4] == 720
    assert capture.properties[5] == 30.0


def test_failed_frame_read_reconnects_safely(monkeypatch: pytest.MonkeyPatch) -> None:
    failed_capture = FakeCapture(reads=[(False, None)])
    reconnected_capture = FakeCapture(
        reads=[(True, np.zeros((2, 2, 3), dtype=np.uint8))]
    )
    captures = iter([failed_capture, reconnected_capture])
    monkeypatch.setattr(
        "src.services.camera_service.cv2.VideoCapture",
        lambda _: next(captures),
    )
    camera = CameraService(reconnect_interval_seconds=0.0)

    assert camera.start()
    assert camera.get_frame() is None
    assert failed_capture.released
    assert camera.get_frame() is not None


def test_camera_rejects_invalid_capture_settings() -> None:
    camera = CameraService()

    assert not camera.set_camera_index(-1)
    assert not camera.set_resolution(0, 720)
    assert not camera.set_fps(0.0)
    assert camera.last_error is not None


def test_capture_reports_write_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    capture = FakeCapture(reads=[(True, np.zeros((2, 2, 3), dtype=np.uint8))])
    monkeypatch.setattr(
        "src.services.camera_service.cv2.VideoCapture", lambda _: capture
    )
    monkeypatch.setattr("src.services.camera_service.cv2.imwrite", lambda *_: False)
    camera = CameraService()

    assert camera.start()
    assert not camera.capture("frame.png")
    assert camera.last_error is not None
