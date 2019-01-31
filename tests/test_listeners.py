from unittest import mock

from region_profiler import RegionProfiler
from region_profiler.debug_listener import DebugListener
from region_profiler.utils import Timer


def test_debug_listener(capsys):
    """Test that debug listener print all necessary data.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = list(range(0, 100, 1))
    rp = RegionProfiler(listeners=[DebugListener()],
                        timer_cls=lambda: Timer(mock_clock))

    @rp.func()
    def foo():
        with rp.region('a'):
            for _ in rp.iter_proxy([1], 'iter'):
                pass

    foo()
    rp.finalize()

    _, err = capsys.readouterr()
    assert 'Entered foo() at 1' in err
    assert 'Entered a at 2' in err
    assert 'Entered iter at 3' in err
    assert 'Exited iter at 4' in err
    assert 'Entered iter at 5' in err
    assert 'Canceled iter at 6' in err
    assert 'Exited iter at 7' in err
    assert 'Exited a at 8' in err
    assert 'Exited foo() at 9' in err
    assert 'Finalizing' in err

