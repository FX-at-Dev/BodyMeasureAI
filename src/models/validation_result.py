"""JSON-safe pose-validation result model."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ValidationStatus(StrEnum):
    """High-level state for a pose-validation result."""

    READY = "ready"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class ValidationResult:
    """Validation outcome for a detected pose."""

    status: ValidationStatus
    message: str
    issues: tuple[str, ...] = ()

    @property
    def is_ready(self) -> bool:
        """Return whether the pose is ready for the next workflow step."""
        return self.status == ValidationStatus.READY

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "status": self.status.value,
            "message": self.message,
            "issues": list(self.issues),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ValidationResult:
        """Create a validation result from a JSON-compatible representation."""
        return cls(
            status=ValidationStatus(data["status"]),
            message=str(data["message"]),
            issues=tuple(str(issue) for issue in data.get("issues", [])),
        )
