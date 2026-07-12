"""Typed application settings and JSON serialization helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CameraSettings:
    """Preferred local-camera capture settings."""

    index: int = 0
    width: int = 1280
    height: int = 720
    fps: float = 30.0


@dataclass(frozen=True)
class AISettings:
    """MediaPipe pose-estimation settings."""

    model_complexity: int = 1
    smooth_landmarks: bool = True
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5


@dataclass(frozen=True)
class UISettings:
    """Desktop presentation settings."""

    theme: str = "dark"
    show_landmark_ids: bool = False


@dataclass(frozen=True)
class ExportSettings:
    """Local export defaults."""

    directory: str = "exports"
    json_indent: int = 2


@dataclass(frozen=True)
class AppSettings:
    """Complete BodyLens configuration grouped by application concern."""

    camera: CameraSettings = CameraSettings()
    ai: AISettings = AISettings()
    ui: UISettings = UISettings()
    export: ExportSettings = ExportSettings()

    def to_dict(self) -> dict[str, Any]:
        """Serialize settings to JSON-compatible primitive values."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> AppSettings:
        """Create settings from JSON data while safely defaulting invalid values."""
        camera_data = _section(data, "camera")
        ai_data = _section(data, "ai")
        ui_data = _section(data, "ui")
        export_data = _section(data, "export")

        return cls(
            camera=CameraSettings(
                index=_integer(camera_data.get("index"), 0, minimum=0),
                width=_integer(camera_data.get("width"), 1280, minimum=1),
                height=_integer(camera_data.get("height"), 720, minimum=1),
                fps=_number(camera_data.get("fps"), 30.0, minimum=0.1),
            ),
            ai=AISettings(
                model_complexity=_integer(
                    ai_data.get("model_complexity"), 1, minimum=0, maximum=2
                ),
                smooth_landmarks=_boolean(ai_data.get("smooth_landmarks"), True),
                min_detection_confidence=_number(
                    ai_data.get("min_detection_confidence"),
                    0.5,
                    minimum=0.0,
                    maximum=1.0,
                ),
                min_tracking_confidence=_number(
                    ai_data.get("min_tracking_confidence"),
                    0.5,
                    minimum=0.0,
                    maximum=1.0,
                ),
            ),
            ui=UISettings(
                theme=_theme(ui_data.get("theme")),
                show_landmark_ids=_boolean(ui_data.get("show_landmark_ids"), False),
            ),
            export=ExportSettings(
                directory=_string(export_data.get("directory"), "exports"),
                json_indent=_integer(export_data.get("json_indent"), 2, minimum=0),
            ),
        )


def _section(data: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    section = data.get(name, {})
    return section if isinstance(section, Mapping) else {}


def _integer(
    value: Any,
    default: int,
    minimum: int,
    maximum: int | None = None,
) -> int:
    if isinstance(value, bool):
        return default

    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default

    if parsed < minimum or (maximum is not None and parsed > maximum):
        return default
    return parsed


def _number(
    value: Any,
    default: float,
    minimum: float,
    maximum: float | None = None,
) -> float:
    if isinstance(value, bool):
        return default

    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default

    if parsed < minimum or (maximum is not None and parsed > maximum):
        return default
    return parsed


def _boolean(value: Any, default: bool) -> bool:
    return value if isinstance(value, bool) else default


def _string(value: Any, default: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else default


def _theme(value: Any) -> str:
    theme = _string(value, "dark").lower()
    return theme if theme in {"dark", "light", "auto"} else "dark"
