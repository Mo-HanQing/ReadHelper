import numpy as np

from readhelper.capture import frame_signature, frames_differ, resize_for_ocr


def test_resize_for_ocr_returns_scale():
    image = np.zeros((1000, 2000, 3), dtype=np.uint8)

    resized, scale = resize_for_ocr(image, 1000)

    assert resized.shape == (500, 1000, 3)
    assert scale == 0.5


def test_frame_difference_detects_meaningful_change():
    first = np.zeros((200, 300, 3), dtype=np.uint8)
    second = first.copy()
    second[40:160, 40:260] = 255

    assert frames_differ(frame_signature(first), frame_signature(second))
    assert not frames_differ(frame_signature(first), frame_signature(first))
