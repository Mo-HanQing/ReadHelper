from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Callable

from PySide6.QtCore import QAbstractNativeEventFilter

WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

VK_NAMES = {
    "SPACE": 0x20,
    "LEFT": 0x25,
    "UP": 0x26,
    "RIGHT": 0x27,
    "DOWN": 0x28,
}


def parse_shortcut(shortcut: str) -> tuple[int, int]:
    parts = [part.strip().upper() for part in shortcut.split("+")]
    modifiers = MOD_NOREPEAT
    key = None
    for part in parts:
        if part in {"CTRL", "CONTROL"}:
            modifiers |= MOD_CONTROL
        elif part == "ALT":
            modifiers |= MOD_ALT
        elif part == "SHIFT":
            modifiers |= MOD_SHIFT
        elif part in {"WIN", "META"}:
            modifiers |= MOD_WIN
        elif len(part) == 1 and part.isalnum():
            key = ord(part)
        elif part in VK_NAMES:
            key = VK_NAMES[part]
        else:
            raise ValueError(f"Unsupported shortcut component: {part}")
    if key is None:
        raise ValueError(f"Shortcut has no key: {shortcut}")
    return modifiers, key


class GlobalHotkeys(QAbstractNativeEventFilter):
    def __init__(self) -> None:
        super().__init__()
        self._callbacks: dict[int, Callable[[], None]] = {}
        self._ids: list[int] = []

    def register(self, hotkey_id: int, shortcut: str, callback: Callable[[], None]) -> bool:
        modifiers, key = parse_shortcut(shortcut)
        registered = bool(
            ctypes.windll.user32.RegisterHotKey(None, hotkey_id, modifiers, key)
        )
        if registered:
            self._ids.append(hotkey_id)
            self._callbacks[hotkey_id] = callback
        return registered

    def unregister_all(self) -> None:
        for hotkey_id in self._ids:
            ctypes.windll.user32.UnregisterHotKey(None, hotkey_id)
        self._ids.clear()
        self._callbacks.clear()

    def nativeEventFilter(self, event_type, message):  # noqa: N802
        if event_type == b"windows_generic_MSG":
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY:
                callback = self._callbacks.get(int(msg.wParam))
                if callback is not None:
                    callback()
                    return True, 0
        return False, 0
