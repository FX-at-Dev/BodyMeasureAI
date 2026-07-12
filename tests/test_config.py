from __future__ import annotations

import json
from pathlib import Path

from src.config.manager import ConfigurationManager
from src.config.settings import AppSettings


def test_configuration_manager_loads_json_settings(tmp_path: Path) -> None:
    config_path = tmp_path / "bodylens.json"
    config_path.write_text(
        json.dumps(
            {
                "camera": {"index": 2, "width": 1920, "height": 1080, "fps": 60},
                "ai": {"model_complexity": 2},
                "ui": {"theme": "light", "show_landmark_ids": True},
                "export": {"directory": "measurement_exports", "json_indent": 4},
            }
        ),
        encoding="utf-8",
    )

    settings = ConfigurationManager(config_path).settings

    assert settings.camera.index == 2
    assert settings.camera.width == 1920
    assert settings.camera.fps == 60.0
    assert settings.ai.model_complexity == 2
    assert settings.ui.theme == "light"
    assert settings.ui.show_landmark_ids
    assert settings.export.directory == "measurement_exports"


def test_configuration_manager_saves_json_settings(tmp_path: Path) -> None:
    config_path = tmp_path / "bodylens.json"
    manager = ConfigurationManager(config_path)

    assert manager.save(AppSettings())
    assert (
        json.loads(config_path.read_text(encoding="utf-8")) == AppSettings().to_dict()
    )
