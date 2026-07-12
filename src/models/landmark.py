"""JSON-safe normalized pose landmark model."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Landmark:
    """A normalized three-dimensional pose point with detection confidence."""

    x: float
    y: float
    z: float
    visibility: float = 1.0
    presence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "visibility": self.visibility,
            "presence": self.presence,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Landmark:
        """Create a landmark from a JSON-compatible representation."""
        presence = data.get("presence")
        return cls(
            x=float(data["x"]),
            y=float(data["y"]),
            z=float(data["z"]),
            visibility=float(data.get("visibility", 1.0)),
            presence=float(presence) if presence is not None else None,
        )
