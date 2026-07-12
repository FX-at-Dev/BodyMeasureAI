"""JSON-safe local export profile model."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ExportFormat(StrEnum):
    """Supported local measurement export formats."""

    JSON = "json"
    CSV = "csv"


@dataclass(frozen=True)
class ExportProfile:
    """Preferences that control a future local export operation."""

    format: ExportFormat
    directory: str = "exports"
    include_pose_data: bool = False
    include_calibration: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "format": self.format.value,
            "directory": self.directory,
            "include_pose_data": self.include_pose_data,
            "include_calibration": self.include_calibration,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ExportProfile:
        """Create an export profile from a JSON-compatible representation."""
        return cls(
            format=ExportFormat(data["format"]),
            directory=str(data.get("directory", "exports")),
            include_pose_data=bool(data.get("include_pose_data", False)),
            include_calibration=bool(data.get("include_calibration", True)),
        )
