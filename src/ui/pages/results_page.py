"""Review page for height and hand measurements."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from src.models.measurement import Measurement, MeasurementKind, MeasurementStatus

if TYPE_CHECKING:
    from src.ui.windows.main_window import MainWindow


class ResultsPage(QWidget):
    """Present supplied measurements with confidence and validation guidance."""

    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self._window = window
        self._title = QLabel("Measurement Review")
        self._height = QLabel("Height: —")
        self._hands = QLabel("Hands: —")
        self._warnings = QLabel("Validation: —")
        self._back_button = QPushButton("Back to Camera")
        self._back_button.clicked.connect(self._window.open_camera)

        for label in (self._title, self._height, self._hands, self._warnings):
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self._title)
        layout.addWidget(self._height)
        layout.addWidget(self._hands)
        layout.addWidget(self._warnings)
        layout.addWidget(self._back_button)
        layout.addStretch()
        self.setLayout(layout)

    def display_height(self, measurement: Measurement) -> None:
        """Display a height-only result without recalculating it in the UI."""
        self.display_measurements((measurement,))

    def display_measurements(self, measurements: tuple[Measurement, ...]) -> None:
        """Display supplied values without running estimation in the UI layer."""
        height = next(
            (
                measurement
                for measurement in measurements
                if measurement.kind == MeasurementKind.HEIGHT
            ),
            None,
        )
        hand_measurements = tuple(
            measurement
            for measurement in measurements
            if measurement.kind != MeasurementKind.HEIGHT
        )
        self._height.setText(self._measurement_text("Height", height))
        self._hands.setText(
            "\n".join(
                self._measurement_text(
                    (
                        f"{measurement.side.value.title() if measurement.side else 'Hand'} "
                        f"{measurement.kind.replace('_', ' ').title()}"
                    ),
                    measurement,
                )
                for measurement in hand_measurements
            )
            or "Hands: —"
        )
        warnings = tuple(
            warning
            for measurement in measurements
            for warning in measurement.validation_warnings
        )
        self._warnings.setText(
            f"Validation: {', '.join(warnings) if warnings else 'Ready'}"
        )

    @staticmethod
    def _measurement_text(label: str, measurement: Measurement | None) -> str:
        """Format one supplied value without making measurement decisions."""
        if measurement is None:
            return f"{label}: —"
        if measurement.status == MeasurementStatus.AVAILABLE:
            return (
                f"{label}: {measurement.value_cm:.1f} {measurement.unit} "
                f"({measurement.confidence:.0%})"
            )
        return f"{label}: Unavailable"
