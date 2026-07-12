"""JSON-safe pose-frame model."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.models.landmark import Landmark


@dataclass(frozen=True)
class PoseFrame:
    """Pose landmarks captured from one camera frame."""

    frame_id: int
    captured_at: datetime
    image_width: int
    image_height: int
    landmarks: tuple[Landmark, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "frame_id": self.frame_id,
            "captured_at": self.captured_at.isoformat(),
            "image_width": self.image_width,
            "image_height": self.image_height,
            "landmarks": [landmark.to_dict() for landmark in self.landmarks],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PoseFrame:
        """Create a pose frame from a JSON-compatible representation."""
        return cls(
            frame_id=int(data["frame_id"]),
            captured_at=datetime.fromisoformat(str(data["captured_at"])),
            image_width=int(data["image_width"]),
            image_height=int(data["image_height"]),
            landmarks=tuple(
                Landmark.from_dict(landmark) for landmark in data.get("landmarks", [])
            ),
        )
