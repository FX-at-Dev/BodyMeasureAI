"""Small presentation-only widget for the active calibration state."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.models.calibration_data import CalibrationData


class CalibrationStatusWidget(QWidget):
    """Show whether local image-scale calibration is currently available."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._status_label = QLabel()
        self._confidence_label = QLabel()
        self._reference_label = QLabel()

        labels = QVBoxLayout()
        labels.addWidget(self._status_label)
        labels.addWidget(self._confidence_label)
        labels.addWidget(self._reference_label)

        layout = QHBoxLayout()
        layout.addLayout(labels)
        layout.addStretch()
        self.setLayout(layout)
        self.set_calibration(None)

    def set_calibration(self, calibration: CalibrationData | None) -> None:
        """Refresh the displayed state without performing calibration work."""
        if calibration is None:
            self._status_label.setText("Calibration: Not Calibrated")
            self._confidence_label.setText("Calibration Confidence: —")
            self._reference_label.setText("Reference: —")
            return

        self._status_label.setText("Calibration: Calibrated")
        self._confidence_label.setText(
            f"Calibration Confidence: {calibration.confidence:.0%}"
        )
        self._reference_label.setText(f"Reference: {calibration.reference_name}")
