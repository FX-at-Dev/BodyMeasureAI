from types import SimpleNamespace

from src.renderers.pose_renderer import PoseRenderer


def test_confidence_color_changes_from_red_to_green() -> None:
    low_confidence = SimpleNamespace(visibility=0.0)
    high_confidence = SimpleNamespace(visibility=1.0)

    low_color = PoseRenderer._confidence_color(low_confidence)
    high_color = PoseRenderer._confidence_color(high_confidence)

    assert low_color.red() > low_color.green()
    assert high_color.green() > high_color.red()
