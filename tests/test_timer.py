from unittest import mock

import pytest

from region_profiler.utils import Timer


@pytest.mark.parametrize('timer_cls', [Timer])
def test_timer_single_shot(timer_cls):
    """Test that ``Timer`` correctly initializes
    its attributes after a single timer shot.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 25]
    t = timer_cls(clock=mock_clock)

    assert t.begin_ts() == 0
    assert t.end_ts() == 0
    assert t.elapsed() == 0
    assert not t.is_running()

    t.start()
    assert t.begin_ts() == 10
    assert t.elapsed() == 0
    assert t.is_running()

    t.stop()
    assert t.begin_ts() == 10
    assert t.end_ts() == 25
    assert t.elapsed() == 15
    assert not t.is_running()


@pytest.mark.parametrize('timer_cls', [Timer])
def test_timer_multiple_shots(timer_cls):
    """Test that ``Timer`` correctly initializes
    its attributes after a multiple timer shots.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 20, 30, 40, 100, 110, 120, 200]
    total = 0

    t = timer_cls(clock=mock_clock)

    assert t.begin_ts() == 0
    assert t.end_ts() == 0
    assert t.elapsed() == 0
    assert not t.is_running()

    t.start()
    assert t.begin_ts() == 10
    assert t.elapsed() == 0
    assert t.is_running()

    t.stop()
    assert t.begin_ts() == 10
    assert t.end_ts() == 20
    assert t.elapsed() == 10
    assert not t.is_running()

    t.start()
    assert t.begin_ts() == 30
    assert t.elapsed() == 0
    assert t.is_running()

    t.start()
    assert t.begin_ts() == 40
    assert t.elapsed() == 0
    assert t.is_running()

    t.stop()
    assert t.begin_ts() == 40
    assert t.end_ts() == 100
    assert t.elapsed() == 60
    assert not t.is_running()

    t.stop()
    assert t.begin_ts() == 40
    assert t.end_ts() == 100
    assert t.elapsed() == 60
    assert not t.is_running()

    t.start()
    assert t.begin_ts() == 120
    assert t.elapsed() == 0
    assert t.is_running()

    t.stop()
    assert t.begin_ts() == 120
    assert t.end_ts() == 200
    assert t.elapsed() == 80
    assert not t.is_running()
