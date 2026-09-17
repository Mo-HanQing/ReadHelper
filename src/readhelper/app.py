from __future__ import annotations

import sys
from enum import IntEnum

from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from .config import ConfigStore, app_data_dir
from .hotkeys import GlobalHotkeys
from .navigation import LineNavigator
from .overlay import FocusOverlay
from .models import DetectedLine, Rect
from .workers import OcrCoordinator, ScreenChangeWatcher


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
        self.ocr = OcrCoordinator(
            app_data_dir() / "paddlex",
            self.config.confidence_threshold,
            self.config.capture_max_width,
            self._current_region,
        )
        self.ocr.completed.connect(self._apply_lines)
        self.ocr.failed.connect(self._show_ocr_error)
        self.ocr.busy_changed.connect(self._set_busy)
        self.watcher = ScreenChangeWatcher(
            self._current_region,
            self.config.change_poll_ms,
            self.config.scroll_settle_ms,
        )
        self.watcher.settled.connect(self.refresh)
        self.hotkeys = GlobalHotkeys()
        application.installNativeEventFilter(self.hotkeys)
        self.tray = QSystemTrayIcon(make_icon(), application)
        self._configure_tray()
        self._register_hotkeys()

    def start(self) -> None:
        self.tray.show()
        self.overlay.show_on_cursor_screen()
        self.watcher.start()
        self.refresh()

    def toggle(self) -> None:
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show_on_cursor_screen()
            self.watcher.reset()
            self.refresh()

    def move_line(self, offset: int) -> None:
        self.overlay.set_active_line(self.navigator.move(offset))

    def refresh(self) -> None:
        if self.overlay.isVisible():
            self.ocr.request()

    def adjust_padding(self, amount: int) -> None:
        self.overlay.adjust_padding(amount)
        self.config_store.save(self.config)

    def shutdown(self) -> None:
        self.watcher.stop()
        self.ocr.stop()
        self.hotkeys.unregister_all()
        self.config_store.save(self.config)
        self.application.quit()

    def _current_region(self) -> Rect:
        geometry = self.overlay.geometry()
        return Rect(geometry.x(), geometry.y(), geometry.width(), geometry.height())

    def _apply_lines(self, lines: list[DetectedLine]) -> None:
        anchor = self.overlay.active_center_y
        current = self.navigator.replace_lines(lines, anchor)
        self.overlay.set_active_line(current)
        if not lines:
            self.tray.setToolTip("ReadHelper - 未检测到文字")
        else:
            self.tray.setToolTip(f"ReadHelper - 已检测 {len(lines)} 行")

    def _show_ocr_error(self, message: str) -> None:
        self.tray.setToolTip("ReadHelper - OCR 失败")
        self.tray.showMessage(
            "ReadHelper OCR 失败",
            message[:240],
            self.tray.MessageIcon.Warning,
            4500,
        )

    def _set_busy(self, busy: bool) -> None:
        if busy:
            self.tray.setToolTip("ReadHelper - 正在识别...")

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
