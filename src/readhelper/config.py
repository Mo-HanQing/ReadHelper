from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from .models import AppConfig, OverlayStyle


def app_data_dir() -> Path:
    override = os.environ.get("READHELPER_DATA_DIR")
    if override:
        return Path(override)
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "ReadHelper"
    return Path.home() / ".readhelper"


def default_config_path() -> Path:
    return app_data_dir() / "config.json"


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_config_path()

    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            style = OverlayStyle(**raw.pop("style", {}))
            return AppConfig(style=style, **raw)
        except (OSError, ValueError, TypeError):
            return AppConfig()

    def save(self, config: AppConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        pending = self.path.with_suffix(".tmp")
        pending.write_text(
            json.dumps(asdict(config), ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
        pending.replace(self.path)
