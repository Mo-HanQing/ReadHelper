from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

from .models import DetectedLine, Rect


def merge_visual_lines(lines: list[DetectedLine]) -> list[DetectedLine]:
    ordered = sorted(lines, key=lambda item: (item.rect.center_y, item.rect.x))
    merged: list[DetectedLine] = []
    for line in ordered:
        if not merged or not _same_row(merged[-1].rect, line.rect):
            merged.append(line)
            continue
        previous = merged[-1]
        left = min(previous.rect.x, line.rect.x)
        top = min(previous.rect.y, line.rect.y)
        right = max(previous.rect.x + previous.rect.width, line.rect.x + line.rect.width)
        bottom = max(previous.rect.bottom, line.rect.bottom)
        merged[-1] = DetectedLine(
            Rect(left, top, right - left, bottom - top),
            max(previous.confidence, line.confidence),
        )
    return merged


def _same_row(first: Rect, second: Rect) -> bool:
    overlap = min(first.bottom, second.bottom) - max(first.y, second.y)
    minimum_height = min(first.height, second.height)
    return overlap > 0 and overlap / max(1, minimum_height) >= 0.45


class OcrEngine:
    def __init__(self, cache_dir: Path, confidence_threshold: float) -> None:
        self.cache_dir = cache_dir
        self.confidence_threshold = confidence_threshold
        self._predictor = None

    def detect(
        self,
        image: np.ndarray,
        origin_x: int,
        origin_y: int,
        scale: float,
    ) -> list[DetectedLine]:
        result = list(self._get_predictor().predict(image))
        if not result:
            return []
        payload = result[0].json.get("res", {})
        polygons = payload.get("dt_polys", [])
        scores = payload.get("dt_scores", [])
        lines: list[DetectedLine] = []
        for polygon, score in zip(polygons, scores):
            confidence = float(score)
            if confidence < self.confidence_threshold:
                continue
            points = np.asarray(polygon, dtype=float)
            left, top = points.min(axis=0)
            right, bottom = points.max(axis=0)
            rect = Rect(
                x=origin_x + round(left / scale),
                y=origin_y + round(top / scale),
                width=max(1, round((right - left) / scale)),
                height=max(1, round((bottom - top) / scale)),
            )
            if rect.height >= 6 and rect.width >= 12:
                lines.append(DetectedLine(rect, confidence))
        return merge_visual_lines(lines)

    def _get_predictor(self):
        if self._predictor is None:
            os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(self.cache_dir))
            os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
            from paddleocr import TextDetection

            bundled = bundled_model_dir()
            arguments = {"model_dir": str(bundled)} if bundled else {
                "model_name": "PP-OCRv6_tiny_det"
            }
            self._predictor = TextDetection(
                **arguments, device="cpu", enable_mkldnn=False
            )
        return self._predictor


def bundled_model_dir() -> Path | None:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if not bundle_root:
        return None
    model_dir = Path(bundle_root) / "models" / "PP-OCRv6_tiny_det"
    return model_dir if model_dir.exists() else None
