from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.ui.windows.main_window import MainWindow


class HomePage(QWidget):
    """Provide the entry point to the live-camera workflow."""

    def __init__(self, window: MainWindow) -> None:
        super().__init__()

        self.main_window = window

        title = QLabel("BodyMeasureAI")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button = QPushButton("Open Camera")
        button.clicked.connect(self.main_window.open_camera)

        layout = QVBoxLayout()

        layout.addStretch()

        layout.addWidget(title)
        layout.addWidget(button)

        layout.addStretch()

        self.setLayout(layout)
