from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
)

from src.ui.pages.home_page import HomePage
from src.ui.pages.camera_page import CameraPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("BodyMeasureAI")
        self.resize(1200, 800)

        self.stack = QStackedWidget()

        self.home = HomePage(self)
        self.camera = CameraPage(self)

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.camera)

        self.setCentralWidget(self.stack)

    def open_camera(self):
        self.stack.setCurrentWidget(self.camera)

    def go_home(self):
        self.stack.setCurrentWidget(self.home)
