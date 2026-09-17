from __future__ import annotations

import sys
from enum import IntEnum

from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from .config import ConfigStore
from .hotkeys import GlobalHotkeys
from .navigation import LineNavigator
from .overlay import FocusOverlay


class HotkeyId(IntEnum):
    TOGGLE = 1
    PREVIOUS = 2
    NEXT = 3
    REFRESH = 4
    SHRINK = 5
    GROW = 6


def make_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor("#16181C"))
    painter = QPainter(pixmap)
    painter.fillRect(3, 13, 26, 6, QColor("#20D8F8"))
    painter.end()
    return QIcon(pixmap)


class ReadHelperApplication:
    def __init__(self, application: QApplication) -> None:
        self.application = application
        self.config_store = ConfigStore()
        self.config = self.config_store.load()
        self.navigator = LineNavigator()
        self.overlay = FocusOverlay(self.config.style)
        self.hotkeys = GlobalHotkeys()
        application.installNativeEventFilter(self.hotkeys)
        self.tray = QSystemTrayIcon(make_icon(), application)
        self._configure_tray()
        self._register_hotkeys()

    def start(self) -> None:
        self.tray.show()
        self.overlay.show_on_cursor_screen()
        self.tray.showMessage("ReadHelper", "阅读聚焦已开启", self.tray.MessageIcon.Information, 1500)

    def toggle(self) -> None:
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show_on_cursor_screen()

    def move_line(self, offset: int) -> None:
        self.overlay.set_active_line(self.navigator.move(offset))

    def refresh(self) -> None:
        self.tray.showMessage("ReadHelper", "OCR 模块将在下一阶段接入", self.tray.MessageIcon.Information, 1200)

    def adjust_padding(self, amount: int) -> None:
        self.overlay.adjust_padding(amount)
        self.config_store.save(self.config)

    def shutdown(self) -> None:
        self.hotkeys.unregister_all()
        self.config_store.save(self.config)
        self.application.quit()

    def _register_hotkeys(self) -> None:
        entries = (
            (HotkeyId.TOGGLE, "toggle", self.toggle),
            (HotkeyId.PREVIOUS, "previous_line", lambda: self.move_line(-1)),
            (HotkeyId.NEXT, "next_line", lambda: self.move_line(1)),
            (HotkeyId.REFRESH, "refresh", self.refresh),
            (HotkeyId.SHRINK, "shrink", lambda: self.adjust_padding(-2)),
            (HotkeyId.GROW, "grow", lambda: self.adjust_padding(2)),
        )
        failed = [
            self.config.shortcuts[name]
            for hotkey_id, name, callback in entries
            if not self.hotkeys.register(hotkey_id, self.config.shortcuts[name], callback)
        ]
        if failed:
            self.tray.showMessage(
                "ReadHelper",
                "快捷键注册失败: " + ", ".join(failed),
                self.tray.MessageIcon.Warning,
                3500,
            )

    def _configure_tray(self) -> None:
        menu = QMenu()
        toggle_action = QAction("开启/关闭聚焦", menu)
        toggle_action.triggered.connect(self.toggle)
        refresh_action = QAction("立即识别", menu)
        refresh_action.triggered.connect(self.refresh)
        exit_action = QAction("退出", menu)
        exit_action.triggered.connect(self.shutdown)
        menu.addAction(toggle_action)
        menu.addAction(refresh_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: self.toggle()
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick
            else None
        )


def main() -> int:
    application = QApplication(sys.argv)
    application.setApplicationName("ReadHelper")
    application.setQuitOnLastWindowClosed(False)
    controller = ReadHelperApplication(application)
    controller.start()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
