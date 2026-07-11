from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class CameraPage(QWidget):

    def __init__(self, window):
        super().__init__()

        self.window = window

        label = QLabel("Camera Coming Soon")

        back = QPushButton("Back")
        back.clicked.connect(window.go_home)

        layout = QVBoxLayout()

        layout.addWidget(label)
        layout.addWidget(back)

        self.setLayout(layout) 