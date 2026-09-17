from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import AppConfig, OverlayStyle


def default_config_path() -> Path:
    return Path.home() / ".readhelper" / "config.json"


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
