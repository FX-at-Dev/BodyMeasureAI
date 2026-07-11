import cv2
from typing import Optional


class CameraService:
    """Handles all communication with the webcam."""

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None

    def start(self) -> bool:
        """Open the camera."""
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_index)

        return self.cap.isOpened()

    def stop(self):
        """Release the camera."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def get_frame(self):
        """Return the latest frame."""

        if self.cap is None:
            return None

        success, frame = self.cap.read()

        if not success:
            return None

        return frame

    def capture(self, filename: str) -> bool:
        """Save the current frame."""

        frame = self.get_frame()

        if frame is None:
            return False

        cv2.imwrite(filename, frame)

        return True

    def is_running(self) -> bool:
        return (
            self.cap is not None
            and self.cap.isOpened()
        )

    def __del__(self):
        self.stop()