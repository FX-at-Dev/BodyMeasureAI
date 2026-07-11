from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class HomePage(QWidget):

    def __init__(self, window):
        super().__init__()

        self.window = window

        title = QLabel("BodyMeasureAI")
        title.setAlignment(Qt.AlignCenter)

        button = QPushButton("Open Camera")
        button.clicked.connect(window.open_camera)

        layout = QVBoxLayout()

        layout.addStretch()

        layout.addWidget(title)
        layout.addWidget(button)

        layout.addStretch()

        self.setLayout(layout)
