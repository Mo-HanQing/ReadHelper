import json
import tempfile
import unittest
from pathlib import Path

from readhelper.config import ConfigStore
from readhelper.models import AppConfig


class ConfigStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "config.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_round_trip_config(self):
        store = ConfigStore(self.path)
        config = AppConfig(scroll_settle_ms=650)
        config.style.dim_opacity = 170
        config.shortcuts["toggle"] = "Ctrl+Shift+Space"

        store.save(config)
        loaded = store.load()

        self.assertEqual(loaded.scroll_settle_ms, 650)
        self.assertEqual(loaded.style.dim_opacity, 170)
        self.assertEqual(loaded.shortcuts["toggle"], "Ctrl+Shift+Space")

    def test_invalid_config_uses_defaults(self):
        self.path.write_text("not json", encoding="utf-8")

        self.assertEqual(ConfigStore(self.path).load(), AppConfig())

    def test_config_is_json(self):
        ConfigStore(self.path).save(AppConfig())

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(raw["style"]["border_width"], 2)

    def test_legacy_mouse_follow_setting_is_migrated(self):
        self.path.write_text('{"mouse_follow_enabled": false}', encoding="utf-8")

        self.assertEqual(ConfigStore(self.path).load().control_mode, "keyboard")

    def test_missing_shortcuts_receive_new_defaults(self):
        self.path.write_text(
            '{"shortcuts": {"toggle": "Ctrl+Shift+Space"}}', encoding="utf-8"
        )

        shortcuts = ConfigStore(self.path).load().shortcuts
        self.assertEqual(shortcuts["toggle"], "Ctrl+Shift+Space")
        self.assertEqual(shortcuts["lock"], "Ctrl+Alt+L")
        self.assertEqual(shortcuts["switch_mode"], "Ctrl+Shift+M")

    def test_unavailable_mode_shortcut_is_migrated(self):
        self.path.write_text(
            '{"shortcuts": {"switch_mode": "Ctrl+Alt+M"}}', encoding="utf-8"
        )

        self.assertEqual(
            ConfigStore(self.path).load().shortcuts["switch_mode"], "Ctrl+Shift+M"
        )


if __name__ == "__main__":
    unittest.main()
