"""JSON-safe optional body-profile metadata."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BodyProfile:
    """User-provided body details that can inform future measurement workflows."""

    profile_id: str
    height_cm: float | None = None
    weight_kg: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "profile_id": self.profile_id,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> BodyProfile:
        """Create a body profile from a JSON-compatible representation."""
        height_cm = data.get("height_cm")
        weight_kg = data.get("weight_kg")
        return cls(
            profile_id=str(data["profile_id"]),
            height_cm=float(height_cm) if height_cm is not None else None,
            weight_kg=float(weight_kg) if weight_kg is not None else None,
        )
