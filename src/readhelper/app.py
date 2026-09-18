from __future__ import annotations

import sys
import logging
from enum import IntEnum

from PySide6.QtCore import QPoint, QTimer
from PySide6.QtGui import QAction, QActionGroup, QColor, QCursor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from .config import ConfigStore, app_data_dir
from .hotkeys import GlobalHotkeys
from .navigation import LineNavigator
from .overlay import FocusOverlay
from .models import DetectedLine, Rect
from .workers import OcrCoordinator, ScreenChangeWatcher
from .settings import SettingsDialog
from .logging_config import configure_logging

logger = logging.getLogger(__name__)


class HotkeyId(IntEnum):
    TOGGLE = 1
    PREVIOUS = 2
    NEXT = 3
    REFRESH = 4
    SHRINK = 5
    GROW = 6
    LOCK = 7


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
        # Persist newly introduced defaults when loading an older config file.
        self.config_store.save(self.config)
        self.navigator = LineNavigator()
        self.is_locked = False
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
        self.mouse_timer = QTimer(application)
        self.mouse_timer.setInterval(self.config.mouse_follow_poll_ms)
        self.mouse_timer.timeout.connect(self._follow_mouse)
        self._last_mouse_position = QCursor.pos()
        self.hotkeys = GlobalHotkeys()
        application.installNativeEventFilter(self.hotkeys)
        self.tray = QSystemTrayIcon(make_icon(), application)
        self._configure_tray()
        self._register_hotkeys()

    def start(self) -> None:
        self.tray.show()
        self.overlay.show_on_cursor_screen()
        self.watcher.start()
        self.mouse_timer.start()
        self.refresh()

    def toggle(self) -> None:
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show_on_cursor_screen()
            self.watcher.reset()
            self.refresh()

    def move_line(self, offset: int) -> None:
        if self.is_locked or self.config.control_mode != "keyboard":
            return
        self.overlay.set_active_line(self.navigator.move(offset))

    def toggle_lock(self) -> None:
        self.is_locked = not self.is_locked
        self.lock_action.setChecked(self.is_locked)
        state = "已锁定当前行" if self.is_locked else "已解锁当前行"
        self.tray.setToolTip(f"ReadHelper - {state}")
        self.tray.showMessage("ReadHelper", state, self.tray.MessageIcon.Information, 1200)

    def refresh(self) -> None:
        if self.overlay.isVisible():
            self.ocr.request()

    def adjust_padding(self, amount: int) -> None:
        self.overlay.adjust_padding(amount)
        self.config_store.save(self.config)

    def show_settings(self) -> None:
        dialog = SettingsDialog(self.config)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        self.config = dialog.result_config()
        self.overlay.style = self.config.style
        self.overlay.update()
        self.watcher.settle_seconds = self.config.scroll_settle_ms / 1000
        self.watcher.timer.setInterval(self.config.change_poll_ms)
        self.ocr.worker.engine.confidence_threshold = self.config.confidence_threshold
        self.mouse_timer.setInterval(self.config.mouse_follow_poll_ms)
        self._sync_mode_actions()
        self.config_store.save(self.config)
        self.hotkeys.unregister_all()
        self._register_hotkeys()

    def shutdown(self) -> None:
        self.mouse_timer.stop()
        self.watcher.stop()
        self.ocr.stop()
        self.hotkeys.unregister_all()
        self.config_store.save(self.config)
        self.application.quit()

    def _current_region(self) -> Rect:
        geometry = self.overlay.geometry()
        return Rect(geometry.x(), geometry.y(), geometry.width(), geometry.height())

    def _apply_lines(self, lines: list[DetectedLine]) -> None:
        logger.info("OCR completed with %d visual lines", len(lines))
        if self.is_locked:
            self.navigator.replace_lines(lines, self.overlay.active_center_y)
            return
        anchor = (
            QCursor.pos().y()
            if self.config.control_mode == "mouse"
            else self.overlay.active_center_y
        )
        current = self.navigator.replace_lines(lines, anchor)
        self.overlay.set_active_line(current)
        if not lines:
            self.tray.setToolTip("ReadHelper - 未检测到文字")
        else:
            self.tray.setToolTip(f"ReadHelper - 已检测 {len(lines)} 行")

    def _show_ocr_error(self, message: str) -> None:
        logger.error("OCR failed\n%s", message)
        self.tray.setToolTip("ReadHelper - OCR 失败")
        self.tray.showMessage(
            "ReadHelper OCR 失败",
            "完整错误已写入 ReadHelper.log",
            self.tray.MessageIcon.Warning,
            4500,
        )

    def _set_busy(self, busy: bool) -> None:
        if busy:
            self.tray.setToolTip("ReadHelper - 正在识别...")

    def _follow_mouse(self) -> None:
        if (
            self.is_locked
            or self.config.control_mode != "mouse"
            or not self.overlay.isVisible()
        ):
            return
        position = QCursor.pos()
        if position == self._last_mouse_position:
            return
        self._last_mouse_position = position
        screen = QApplication.screenAt(position)
        if screen is None:
            return
        screen_geometry = screen.geometry()
        if screen_geometry != self.overlay.geometry():
            self.overlay.show_on_cursor_screen()
            self.navigator.replace_lines([])
            self.overlay.set_active_line(None)
            self.watcher.reset()
            self.refresh()
            return
        line = self.navigator.select_nearest_y(position.y())
        if line is not None and line != self.overlay.active_line:
            self.overlay.set_active_line(line)

    def set_control_mode(self, mode: str) -> None:
        if mode not in {"mouse", "keyboard"}:
            return
        self.config.control_mode = mode
        self.config_store.save(self.config)
        self._sync_mode_actions()
        if mode == "mouse":
            self._last_mouse_position = QCursor.pos() + QPoint(1, 1)
            self._follow_mouse()

    def _sync_mode_actions(self) -> None:
        for mode, action in self.mode_actions.items():
            action.setChecked(self.config.control_mode == mode)

    def _register_hotkeys(self) -> None:
        entries = (
            (HotkeyId.TOGGLE, "toggle", self.toggle),
            (HotkeyId.PREVIOUS, "previous_line", lambda: self.move_line(-1)),
            (HotkeyId.NEXT, "next_line", lambda: self.move_line(1)),
            (HotkeyId.REFRESH, "refresh", self.refresh),
            (HotkeyId.LOCK, "lock", self.toggle_lock),
            (HotkeyId.SHRINK, "shrink", lambda: self.adjust_padding(-2)),
            (HotkeyId.GROW, "grow", lambda: self.adjust_padding(2)),
        )
        failed = []
        for hotkey_id, name, callback in entries:
            shortcut = self.config.shortcuts[name]
            if self.hotkeys.register(hotkey_id, shortcut, callback):
                logger.info("Registered hotkey %s: %s", name, shortcut)
            else:
                logger.error("Failed to register hotkey %s: %s", name, shortcut)
                failed.append(shortcut)
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
        self.lock_action = QAction("锁定当前行", menu)
        self.lock_action.setCheckable(True)
        self.lock_action.triggered.connect(self.toggle_lock)
        mode_menu = QMenu("控制模式", menu)
        mode_group = QActionGroup(mode_menu)
        mode_group.setExclusive(True)
        self.mode_actions = {}
        for mode, label in (("mouse", "鼠标跟随"), ("keyboard", "键盘控制")):
            action = QAction(label, mode_menu)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked=False, value=mode: self.set_control_mode(value)
            )
            mode_group.addAction(action)
            mode_menu.addAction(action)
            self.mode_actions[mode] = action
        self._sync_mode_actions()
        settings_action = QAction("设置...", menu)
        settings_action.triggered.connect(self.show_settings)
        exit_action = QAction("退出", menu)
        exit_action.triggered.connect(self.shutdown)
        menu.addAction(toggle_action)
        menu.addAction(refresh_action)
        menu.addAction(self.lock_action)
        menu.addMenu(mode_menu)
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: self.toggle()
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick
            else None
        )


def main() -> int:
    configure_logging()
    logger.info("ReadHelper starting")
    application = QApplication(sys.argv)
    application.setApplicationName("ReadHelper")
    application.setQuitOnLastWindowClosed(False)
    controller = ReadHelperApplication(application)
    controller.start()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
