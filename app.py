import sys
from os import environ

import qdarktheme
from PySide6.QtWidgets import QApplication

from src.config import load_settings
from src.ui.windows.main_window import MainWindow
from src.utils.logger import configure_logging


def main() -> int:
    """Start the BodyLens desktop application."""
    settings = load_settings()
    configure_logging(debug=environ.get("BODYLENS_DEBUG") == "1")

    app = QApplication(sys.argv)

    qdarktheme.setup_theme(settings.ui.theme)

    window = MainWindow()

    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
