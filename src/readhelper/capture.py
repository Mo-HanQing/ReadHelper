from __future__ import annotations

import cv2
import mss
import numpy as np

from .models import Rect


def capture_region(region: Rect) -> np.ndarray:
    monitor = {
        "left": region.x,
        "top": region.y,
        "width": region.width,
        "height": region.height,
    }
    with mss.mss() as capturer:
        bgra = np.asarray(capturer.grab(monitor))
    return np.ascontiguousarray(bgra[:, :, :3])


def resize_for_ocr(image: np.ndarray, max_width: int) -> tuple[np.ndarray, float]:
    if image.shape[1] <= max_width:
        return image, 1.0
    scale = max_width / image.shape[1]
    resized = cv2.resize(
        image,
        (max_width, max(1, round(image.shape[0] * scale))),
        interpolation=cv2.INTER_AREA,
    )
    return resized, scale


def frame_signature(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.resize(gray, (96, 54), interpolation=cv2.INTER_AREA)


def frames_differ(previous: np.ndarray, current: np.ndarray, threshold: float = 2.5) -> bool:
    difference = cv2.absdiff(previous, current)
    return float(np.mean(difference)) >= threshold
