from unittest import mock

from region_profiler.utils import Timer


def test_timer_single_shot():
    """Test that ``Timer`` correctly initializes
    its attributes after a single timer shot.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 20, 30]
    t = Timer(clock=mock_clock)
    assert t.current_elapsed() == 0
    assert t.total_elapsed() == 0
    t.start()
    assert t.current_elapsed() == 10
    t.stop()
    assert t.current_elapsed() == 0
    assert t.total_elapsed() == 20
