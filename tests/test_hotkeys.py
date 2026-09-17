import pytest

from readhelper.hotkeys import MOD_ALT, MOD_CONTROL, MOD_NOREPEAT, parse_shortcut


def test_parse_shortcut():
    modifiers, key = parse_shortcut("Ctrl+Alt+R")

    assert modifiers == MOD_CONTROL | MOD_ALT | MOD_NOREPEAT
    assert key == ord("R")


def test_parse_shortcut_rejects_unknown_key():
    with pytest.raises(ValueError):
        parse_shortcut("Ctrl+PageDown")
