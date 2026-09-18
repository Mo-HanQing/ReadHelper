from __future__ import annotations

from copy import deepcopy

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .hotkeys import parse_shortcut
from .models import AppConfig

SHORTCUT_LABELS = {
    "toggle": "开启/关闭聚焦",
    "previous_line": "上一行",
    "next_line": "下一行",
    "refresh": "立即识别",
    "lock": "锁定/解锁当前行",
    "shrink": "减小阅读带",
    "grow": "增大阅读带",
}


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self._source = config
        self._color = config.style.border_color
        self.shortcut_edits: dict[str, QLineEdit] = {}
        self.setWindowTitle("ReadHelper 设置")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(self._appearance_tab(config), "外观")
        tabs.addTab(self._behavior_tab(config), "识别")
        tabs.addTab(self._shortcuts_tab(config), "快捷键")
        layout.addWidget(tabs)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #c43b3b;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("保存")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def result_config(self) -> AppConfig:
        config = deepcopy(self._source)
        config.style.dim_opacity = self.opacity.value()
        config.style.border_color = self._color
        config.style.border_width = self.border_width.value()
        config.style.vertical_padding = self.padding.value()
        config.confidence_threshold = self.confidence.value()
        config.scroll_settle_ms = self.settle_ms.value()
        config.change_poll_ms = self.poll_ms.value()
        config.control_mode = self.control_mode.currentData()
        config.shortcuts = {
            name: editor.text().strip() for name, editor in self.shortcut_edits.items()
        }
        return config

    def _appearance_tab(self, config: AppConfig) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        self.opacity = QSlider(Qt.Orientation.Horizontal)
        self.opacity.setRange(20, 230)
        self.opacity.setValue(config.style.dim_opacity)
        form.addRow("遮罩暗度", self.opacity)
        self.color_button = QPushButton(config.style.border_color)
        self.color_button.clicked.connect(self._choose_color)
        self._update_color_button()
        form.addRow("边界线颜色", self.color_button)
        self.border_width = QSpinBox()
        self.border_width.setRange(1, 8)
        self.border_width.setValue(config.style.border_width)
        self.border_width.setSuffix(" px")
        form.addRow("边界线粗细", self.border_width)
        self.padding = QSpinBox()
        self.padding.setRange(0, 80)
        self.padding.setValue(config.style.vertical_padding)
        self.padding.setSuffix(" px")
        form.addRow("行上下留白", self.padding)
        return tab

    def _behavior_tab(self, config: AppConfig) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        self.control_mode = QComboBox()
        self.control_mode.addItem("鼠标跟随", "mouse")
        self.control_mode.addItem("键盘控制", "keyboard")
        selected = self.control_mode.findData(config.control_mode)
        self.control_mode.setCurrentIndex(max(0, selected))
        form.addRow("控制模式", self.control_mode)
        self.confidence = QDoubleSpinBox()
        self.confidence.setRange(0.1, 0.95)
        self.confidence.setSingleStep(0.05)
        self.confidence.setValue(config.confidence_threshold)
        form.addRow("文字检测置信度", self.confidence)
        self.settle_ms = QSpinBox()
        self.settle_ms.setRange(150, 2000)
        self.settle_ms.setValue(config.scroll_settle_ms)
        self.settle_ms.setSuffix(" ms")
        form.addRow("滚动停止等待", self.settle_ms)
        self.poll_ms = QSpinBox()
        self.poll_ms.setRange(100, 1000)
        self.poll_ms.setValue(config.change_poll_ms)
        self.poll_ms.setSuffix(" ms")
        form.addRow("画面检查间隔", self.poll_ms)
        return tab

    def _shortcuts_tab(self, config: AppConfig) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        for name, label in SHORTCUT_LABELS.items():
            editor = QLineEdit(config.shortcuts[name])
            self.shortcut_edits[name] = editor
            form.addRow(label, editor)
        return tab

    def _choose_color(self) -> None:
        selected = QColorDialog.getColor(QColor(self._color), self, "选择边界线颜色")
        if selected.isValid():
            self._color = selected.name()
            self.color_button.setText(self._color)
            self._update_color_button()

    def _update_color_button(self) -> None:
        color = QColor(self._color)
        text_color = "#000000" if color.lightness() > 150 else "#ffffff"
        self.color_button.setStyleSheet(
            f"background-color: {self._color}; color: {text_color};"
        )

    def _validate_and_accept(self) -> None:
        try:
            for editor in self.shortcut_edits.values():
                parse_shortcut(editor.text())
        except ValueError as error:
            self.error_label.setText(str(error))
            return
        normalized = [editor.text().replace(" ", "").upper() for editor in self.shortcut_edits.values()]
        if len(normalized) != len(set(normalized)):
            self.error_label.setText("快捷键不能重复")
            return
        self.accept()
