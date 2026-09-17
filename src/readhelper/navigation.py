from __future__ import annotations

from .models import DetectedLine


class LineNavigator:
    def __init__(self) -> None:
        self._lines: list[DetectedLine] = []
        self._index = -1

    @property
    def lines(self) -> tuple[DetectedLine, ...]:
        return tuple(self._lines)

    @property
    def current(self) -> DetectedLine | None:
        if 0 <= self._index < len(self._lines):
            return self._lines[self._index]
        return None

    def replace_lines(
        self, lines: list[DetectedLine], anchor_y: float | None = None
    ) -> DetectedLine | None:
        previous = self.current
        self._lines = sorted(lines, key=lambda line: (line.rect.center_y, line.rect.x))
        if not self._lines:
            self._index = -1
            return None
        target_y = anchor_y
        if target_y is None and previous is not None:
            target_y = previous.rect.center_y
        if target_y is None:
            self._index = len(self._lines) // 2
        else:
            self._index = min(
                range(len(self._lines)),
                key=lambda index: abs(self._lines[index].rect.center_y - target_y),
            )
        return self.current

    def move(self, offset: int) -> DetectedLine | None:
        if not self._lines:
            return None
        self._index = max(0, min(len(self._lines) - 1, self._index + offset))
        return self.current
