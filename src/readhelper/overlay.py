from __future__ import annotations

import ctypes

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QCursor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QWidget

from .models import DetectedLine, OverlayStyle

WDA_EXCLUDEFROMCAPTURE = 0x00000011


class FocusOverlay(QWidget):
    def __init__(self, style: OverlayStyle) -> None:
        super().__init__()
        self.style = style
        self._active_line: DetectedLine | None = None
        self._fallback_center = 0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )

    @property
    def active_center_y(self) -> float:
        if self._active_line is not None:
            return self._active_line.rect.center_y
        return float(self._fallback_center)

    @property
    def active_line(self) -> DetectedLine | None:
        return self._active_line

    def show_on_cursor_screen(self) -> None:
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.geometry()
        self.setGeometry(geometry)
        if not self._fallback_center:
            self._fallback_center = geometry.height() // 2
        self.show()
        self.raise_()
        try:
            ctypes.windll.user32.SetWindowDisplayAffinity(
                int(self.winId()), WDA_EXCLUDEFROMCAPTURE
            )
        except OSError:
            pass
        self.update()

    def set_active_line(self, line: DetectedLine | None) -> None:
        self._active_line = line
        self.update()

    def adjust_padding(self, amount: int) -> None:
        self.style.vertical_padding = max(0, min(80, self.style.vertical_padding + amount))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        band = self._band_rect()
        dim = QColor(0, 0, 0, self.style.dim_opacity)
        painter.fillRect(QRect(0, 0, self.width(), max(0, band.top())), dim)
        painter.fillRect(
            QRect(0, band.bottom() + 1, self.width(), max(0, self.height() - band.bottom())),
            dim,
        )
        pen = QPen(QColor(self.style.border_color), self.style.border_width)
        painter.setPen(pen)
        painter.drawLine(0, band.top(), self.width(), band.top())
        painter.drawLine(0, band.bottom(), self.width(), band.bottom())

    def _band_rect(self) -> QRect:
        if self._active_line is None:
            height = 36 + self.style.vertical_padding * 2
            top = self._fallback_center - height // 2
        else:
            top = self._active_line.rect.y - self.geometry().y() - self.style.vertical_padding
            height = self._active_line.rect.height + self.style.vertical_padding * 2
        top = max(0, min(self.height() - 1, top))
        height = max(1, min(self.height() - top, height))
        return QRect(0, top, self.width(), height)
