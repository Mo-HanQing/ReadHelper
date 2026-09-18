from readhelper.models import AppConfig
from readhelper.settings import SettingsDialog


def test_settings_dialog_builds_config(qtbot):
    source = AppConfig()
    dialog = SettingsDialog(source)
    qtbot.addWidget(dialog)
    dialog.opacity.setValue(180)
    dialog.padding.setValue(12)
    dialog.control_mode.setCurrentIndex(dialog.control_mode.findData("keyboard"))
    dialog.shortcut_edits["toggle"].setText("Ctrl+Shift+Space")

    result = dialog.result_config()

    assert result.style.dim_opacity == 180
    assert result.style.vertical_padding == 12
    assert result.shortcuts["toggle"] == "Ctrl+Shift+Space"
    assert result.control_mode == "keyboard"
    assert source.style.dim_opacity == 140
