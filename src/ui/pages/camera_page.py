from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.ui.widgets.camera_widget import CameraWidget


class CameraPage(QWidget):

    def __init__(self, window):
        super().__init__()

        self.window = window

        self.camera = CameraWidget()

        self.status = QLabel("🟢 Camera Ready")

        self.capture_button = QPushButton("📸 Capture")

        self.import_button = QPushButton("📂 Import")

        self.back_button = QPushButton("⬅ Back")

        self.back_button.clicked.connect(window.go_home)

        buttons = QHBoxLayout()
        buttons.addWidget(self.import_button)
        buttons.addWidget(self.capture_button)
        buttons.addStretch()
        buttons.addWidget(self.back_button)

        layout = QVBoxLayout()

        layout.addWidget(self.status)
        self.camera.setMinimumSize(800, 600)
        layout.addWidget(self.camera)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def showEvent(self, event):

        self.camera.start()

        super().showEvent(event)

    def hideEvent(self, event):

        self.camera.stop()

        super().hideEvent(event)