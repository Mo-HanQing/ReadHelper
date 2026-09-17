import numpy as np

from readhelper.models import DetectedLine, Rect
from readhelper.ocr import OcrEngine, merge_visual_lines


def test_merge_visual_lines_combines_fragments_on_same_row():
    lines = [
        DetectedLine(Rect(10, 100, 100, 20), 0.8),
        DetectedLine(Rect(160, 102, 120, 18), 0.9),
        DetectedLine(Rect(10, 150, 200, 20), 0.85),
    ]

    merged = merge_visual_lines(lines)

    assert len(merged) == 2
    assert merged[0].rect == Rect(10, 100, 270, 20)
    assert merged[0].confidence == 0.9


class FakeResult:
    json = {
        "res": {
            "dt_polys": [[[10, 20], [110, 20], [110, 40], [10, 40]]],
            "dt_scores": [0.91],
        }
    }


class FakePredictor:
    def predict(self, image):
        return [FakeResult()]


def test_ocr_engine_maps_scaled_coordinates():
    engine = OcrEngine.__new__(OcrEngine)
    engine.confidence_threshold = 0.45
    engine._predictor = FakePredictor()

    lines = engine.detect(np.zeros((10, 10, 3)), 100, 200, 0.5)

    assert lines[0].rect == Rect(120, 240, 200, 40)
