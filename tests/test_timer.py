from unittest import mock

from region_profiler.utils import Timer


def test_timer_single_shot():
    """Test that ``Timer`` correctly initializes
    its attributes after a single timer shot.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 20, 22, 30]
    t = Timer(clock=mock_clock)
    assert t.current_elapsed() == 0
    assert t.total_elapsed() == 0
    assert not t.is_running()
    t.start()
    assert t.current_elapsed() == 10
    assert t.total_elapsed() == 12
    assert t.is_running()
    t.stop()
    assert t.current_elapsed() == 0
    assert t.total_elapsed() == 20
    assert not t.is_running()


def test_timer_multiple_shots():
    """Test that ``Timer`` correctly initializes
    its attributes after a multiple timer shots.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 20, 30, 100, 120, 140, 200, 300, 400]
    total = 0

    t = Timer(clock=mock_clock)
    assert t.current_elapsed() == 0
    assert t.total_elapsed() == total
    assert not t.is_running()

    t.start()
    assert t.current_elapsed() == 10
    assert t.is_running()
    t.stop()
    total += 20
    assert t.current_elapsed() == 0
    assert t.total_elapsed() == total
    assert not t.is_running()

    t.start()
    assert t.current_elapsed() == 20
    assert t.is_running()
    t.stop()
    total += 40
    assert t.current_elapsed() == 0
    assert t.total_elapsed() == total
    assert not t.is_running()

    t.start()
    assert t.current_elapsed() == 100
    assert t.is_running()
    t.stop()
    total += 200
    assert t.current_elapsed() == 0
    assert t.total_elapsed() == total
    assert not t.is_running()
