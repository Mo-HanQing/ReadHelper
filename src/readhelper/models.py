from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    @property
    def bottom(self) -> int:
        return self.y + self.height


@dataclass(frozen=True, slots=True)
class DetectedLine:
    rect: Rect
    confidence: float = 1.0


@dataclass(slots=True)
class OverlayStyle:
    dim_opacity: int = 140
    border_color: str = "#20D8F8"
    border_width: int = 2
    vertical_padding: int = 4


@dataclass(slots=True)
class AppConfig:
    style: OverlayStyle = field(default_factory=OverlayStyle)
    confidence_threshold: float = 0.45
    scroll_settle_ms: int = 400
    change_poll_ms: int = 180
    capture_max_width: int = 1600
    control_mode: str = "mouse"
    mouse_follow_poll_ms: int = 32
    shortcuts: dict[str, str] = field(
        default_factory=lambda: {
            "toggle": "Ctrl+Alt+Space",
            "previous_line": "Alt+Up",
            "next_line": "Alt+Down",
            "refresh": "Ctrl+Alt+R",
            "shrink": "Ctrl+Alt+Left",
            "grow": "Ctrl+Alt+Right",
        }
    )
