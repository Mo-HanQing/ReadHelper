from __future__ import annotations

import time
import traceback
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from .capture import capture_region, frame_signature, frames_differ, resize_for_ocr
from .models import DetectedLine, Rect
from .ocr import OcrEngine


class OcrWorker(QObject):
    completed = Signal(list)
    failed = Signal(str)

    def __init__(self, engine: OcrEngine, max_width: int) -> None:
        super().__init__()
        self.engine = engine
        self.max_width = max_width

    @Slot(object)
    def process(self, region: Rect) -> None:
        try:
            image = capture_region(region)
            image, scale = resize_for_ocr(image, self.max_width)
            lines = self.engine.detect(image, region.x, region.y, scale)
            self.completed.emit(lines)
        except Exception:  # The GUI must survive OCR/runtime failures.
            self.failed.emit(traceback.format_exc())


class OcrCoordinator(QObject):
    requested = Signal(object)
    completed = Signal(list)
    failed = Signal(str)
    busy_changed = Signal(bool)

    def __init__(
        self,
        cache_dir: Path,
        confidence_threshold: float,
        max_width: int,
        region_provider: Callable[[], Rect],
    ) -> None:
        super().__init__()
        self.region_provider = region_provider
        self._busy = False
        self._pending = False
        self.thread = QThread(self)
        self.worker = OcrWorker(
            OcrEngine(cache_dir, confidence_threshold),
            max_width,
        )
        self.worker.moveToThread(self.thread)
        self.requested.connect(self.worker.process)
        self.worker.completed.connect(self._on_completed)
        self.worker.failed.connect(self._on_failed)
        self.thread.start()

    def request(self) -> None:
        if self._busy:
            self._pending = True
            return
        self._busy = True
        self.busy_changed.emit(True)
        self.requested.emit(self.region_provider())

    def stop(self) -> None:
        self.thread.quit()
        self.thread.wait(5000)

    @Slot(list)
    def _on_completed(self, lines: list[DetectedLine]) -> None:
        self.completed.emit(lines)
        self._finish_request()

    @Slot(str)
    def _on_failed(self, message: str) -> None:
        self.failed.emit(message)
        self._finish_request()

    def _finish_request(self) -> None:
        self._busy = False
        self.busy_changed.emit(False)
        if self._pending:
            self._pending = False
            QTimer.singleShot(0, self.request)


class ScreenChangeWatcher(QObject):
    settled = Signal()

    def __init__(
        self,
        region_provider: Callable[[], Rect],
        poll_ms: int,
        settle_ms: int,
    ) -> None:
        super().__init__()
        self.region_provider = region_provider
        self.settle_seconds = settle_ms / 1000
        self._previous = None
        self._changed_at: float | None = None
        self._emitted_for_change = False
        self.timer = QTimer(self)
        self.timer.setInterval(poll_ms)
        self.timer.timeout.connect(self._poll)

    def start(self) -> None:
        self.timer.start()

    def stop(self) -> None:
        self.timer.stop()

    def reset(self) -> None:
        self._previous = None
        self._changed_at = None
        self._emitted_for_change = False

    def _poll(self) -> None:
        try:
            signature = frame_signature(capture_region(self.region_provider()))
        except Exception:
            return
        if self._previous is None:
            self._previous = signature
            return
        if frames_differ(self._previous, signature):
            self._changed_at = time.monotonic()
            self._emitted_for_change = False
        elif (
            self._changed_at is not None
            and not self._emitted_for_change
            and time.monotonic() - self._changed_at >= self.settle_seconds
        ):
            self._emitted_for_change = True
            self.settled.emit()
        self._previous = signature
