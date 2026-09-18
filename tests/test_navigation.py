from readhelper.models import DetectedLine, Rect
from readhelper.navigation import LineNavigator


def line(y, x=0):
    return DetectedLine(Rect(x=x, y=y, width=100, height=20), 0.9)


def test_replace_lines_sorts_and_selects_nearest_anchor():
    navigator = LineNavigator()

    current = navigator.replace_lines([line(300), line(100), line(200)], anchor_y=215)

    assert [item.rect.y for item in navigator.lines] == [100, 200, 300]
    assert current.rect.y == 200


def test_navigation_clamps_at_edges():
    navigator = LineNavigator()
    navigator.replace_lines([line(100), line(200)], anchor_y=100)

    assert navigator.move(-1).rect.y == 100
    assert navigator.move(1).rect.y == 200
    assert navigator.move(1).rect.y == 200


def test_empty_lines_clear_selection():
    navigator = LineNavigator()
    navigator.replace_lines([line(100)])

    assert navigator.replace_lines([]) is None
    assert navigator.current is None


def test_refresh_without_anchor_preserves_previous_vertical_position():
    navigator = LineNavigator()
    navigator.replace_lines([line(100), line(300)], anchor_y=300)

    current = navigator.replace_lines([line(90), line(290), line(490)])

    assert current.rect.y == 290


def test_select_nearest_y_follows_cursor_position():
    navigator = LineNavigator()
    navigator.replace_lines([line(100), line(200), line(300)], anchor_y=100)

    assert navigator.select_nearest_y(225).rect.y == 200
    assert navigator.select_nearest_y(295).rect.y == 300
