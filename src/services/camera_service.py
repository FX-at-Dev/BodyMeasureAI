"""Resilient local webcam access with configurable capture settings."""

from __future__ import annotations

from pathlib import Path
from time import monotonic
from typing import cast

import cv2
import numpy as np
from numpy.typing import NDArray

from src.utils.logger import logger

Frame = NDArray[np.uint8]
Resolution = tuple[int, int]


class CameraService:
    """Manage a local OpenCV camera with safe reconnect and configuration APIs."""

    def __init__(
        self,
        camera_index: int = 0,
        resolution: Resolution | None = None,
        fps: float | None = None,
        reconnect_interval_seconds: float = 1.0,
    ) -> None:
        self.camera_index = camera_index
        self.cap: cv2.VideoCapture | None = None
        self.resolution = resolution
        self.fps = fps
        self.last_error: str | None = None
        self._reconnect_interval_seconds = max(0.0, reconnect_interval_seconds)
        self._last_reconnect_attempt = float("-inf")

    def start(self) -> bool:
        """Open the selected camera and apply the configured capture settings."""
        if self.is_running():
            return True

        self.stop()

        try:
            capture = cv2.VideoCapture(self.camera_index)
            if not capture.isOpened():
                capture.release()
                self._record_error(f"Unable to open camera index {self.camera_index}.")
                return False

            self.cap = capture
            self._apply_settings()
            self.last_error = None
            logger.info("Camera index %s started.", self.camera_index)
            return True
        except Exception as error:
            self._record_error(
                f"Unable to start camera index {self.camera_index}: {error}"
            )
            self.stop()
            return False

    def stop(self) -> None:
        """Release the current camera handle without raising driver errors."""
        if self.cap is None:
            return

        capture = self.cap
        self.cap = None

        try:
            capture.release()
        except Exception as error:
            logger.warning(
                "Unable to release camera index %s: %s", self.camera_index, error
            )

    def set_camera_index(self, camera_index: int) -> bool:
        """Select a camera device, reopening capture if it is currently active."""
        if camera_index < 0:
            self._record_error("Camera index must be zero or greater.")
            return False

        if camera_index == self.camera_index:
            return True

        was_running = self.is_running()
        self.stop()
        self.camera_index = camera_index
        return self.start() if was_running else True

    def set_resolution(self, width: int, height: int) -> bool:
        """Configure the requested frame resolution for future and active capture."""
        if width <= 0 or height <= 0:
            self._record_error("Camera resolution dimensions must be positive.")
            return False

        self.resolution = (width, height)
        return self._apply_settings()

    def set_fps(self, fps: float) -> bool:
        """Configure the requested capture frame rate for future and active capture."""
        if fps <= 0:
            self._record_error("Camera FPS must be greater than zero.")
            return False

        self.fps = fps
        return self._apply_settings()

    def reconnect(self) -> bool:
        """Release and reopen the selected camera when a driver connection is lost."""
        self._last_reconnect_attempt = monotonic()
        logger.info("Reconnecting camera index %s.", self.camera_index)
        self.stop()
        return self.start()

    def get_frame(self) -> Frame | None:
        """Return the latest frame, reconnecting safely after a failed read."""
        if not self.is_running():
            self._attempt_reconnect()
            return None

        try:
            success, frame = self.cap.read() if self.cap is not None else (False, None)
        except Exception as error:
            self._record_error(f"Unable to read camera frame: {error}")
            self._attempt_reconnect()
            return None

        if not success or frame is None:
            self._record_error("Camera frame read failed.")
            self._attempt_reconnect()
            return None

        self.last_error = None
        return cast(Frame, frame)

    def capture(self, filename: str | Path) -> bool:
        """Save the latest camera frame and report local write failures safely."""
        frame = self.get_frame()

        if frame is None:
            return False

        try:
            if cv2.imwrite(str(filename), frame):
                return True
        except Exception as error:
            self._record_error(f"Unable to save camera frame: {error}")
            return False

        self._record_error(f"Unable to save camera frame to {filename}.")
        return False

    def is_running(self) -> bool:
        """Return whether the current camera handle is open and usable."""
        if self.cap is None:
            return False

        try:
            return bool(self.cap.isOpened())
        except Exception as error:
            self._record_error(f"Unable to inspect camera state: {error}")
            return False

    def _apply_settings(self) -> bool:
        """Apply requested resolution and FPS to an active capture when available."""
        if self.cap is None:
            return True

        try:
            if self.resolution is not None:
                width, height = self.resolution
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            if self.fps is not None:
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)

            return True
        except Exception as error:
            self._record_error(f"Unable to apply camera settings: {error}")
            return False

    def _attempt_reconnect(self) -> None:
        if (
            monotonic() - self._last_reconnect_attempt
            < self._reconnect_interval_seconds
        ):
            return

        self.reconnect()

    def _record_error(self, message: str) -> None:
        self.last_error = message
        logger.warning(message)

    def __del__(self) -> None:
        self.stop()
