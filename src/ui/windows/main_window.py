from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
)

from src.ui.pages.camera_page import CameraPage
from src.ui.pages.home_page import HomePage


class MainWindow(QMainWindow):
    """Host the application's top-level pages."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("BodyMeasureAI")
        self.resize(1200, 800)

        self.stack = QStackedWidget()

        self.home = HomePage(self)
        self.camera = CameraPage(self)
        self.camera.shutdown_finished.connect(self._close_after_camera_shutdown)

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.camera)

        self.setCentralWidget(self.stack)

    def open_camera(self) -> None:
        """Display the live-camera page."""
        self.stack.setCurrentWidget(self.camera)

    def go_home(self) -> None:
        """Display the home page."""
        self.stack.setCurrentWidget(self.home)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Release the camera worker before destroying the window."""
        if self.camera.shutdown():
            super().closeEvent(event)
            return

        event.ignore()

    def _close_after_camera_shutdown(self) -> None:
        self.close()
