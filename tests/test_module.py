import atexit
import contextlib
import time
from unittest import mock

import pytest

from region_profiler import region, func, install as install_profiler, iter_proxy, Timer, RegionProfiler
import region_profiler.profiler
from region_profiler.reporters import SilentReporter
from region_profiler import reporter_columns as cols


@contextlib.contextmanager
def fresh_region_profiler(monkeypatch):
    """Reset ``region_profiler`` module before a next integration test.
    """
    region_profiler.profiler._profiler = None
    atexit_functions = []
    monkeypatch.setattr(atexit, 'register', lambda foo: atexit_functions.append(foo))
    yield None
    for callback in reversed(atexit_functions):
        callback()
    return


@pytest.mark.parametrize('multiple_runs', [0, 1, 2])
def test_reload_works(monkeypatch, multiple_runs):
    """Test that ``fresh_module`` fixture properly
    resets ``region_profiler`` module.
    """
    reporter = SilentReporter([cols.name])
    with fresh_region_profiler(monkeypatch):
        assert region_profiler.profiler._profiler is None
        install_profiler(reporter)
        assert isinstance(region_profiler.profiler._profiler, region_profiler.RegionProfiler)
    assert reporter.rows == [['name'], [RegionProfiler.ROOT_NODE_NAME]]


def test_with_fake_timer(monkeypatch):
    """Integration test with a fake timer.
    """
    reporter = SilentReporter([cols.name, cols.total_us, cols.total_inner_us, cols.count])
    mock_clock = mock.Mock()
    mock_clock.side_effect = list(range(0, 100, 1))

    @func()
    def foo():
        with region('a'):
            for i in iter_proxy([1, 2, 3], 'iter'):
                with region('b'):
                    pass
                with region('b'):
                    pass

    with fresh_region_profiler(monkeypatch):
        install_profiler(reporter=reporter, timer_cls=lambda: Timer(mock_clock))
        foo()
        with region('x'):
            pass
        foo()

    expected = [['name', 'total_us', 'total_inner_us', 'count'],
                [RegionProfiler.ROOT_NODE_NAME, '49000000', '4000000', '1'],
                ['foo()', '44000000', '4000000', '2'],
                ['a', '40000000', '22000000', '2'],
                ['b', '12000000', '12000000', '12'],
                ['iter', '6000000', '6000000', '6'],
                ['x', '1000000', '1000000', '1']]

    assert reporter.rows == expected


def test_with_real_timer(monkeypatch):
    """Integration test with a real timer.
    """
    reporter = SilentReporter([cols.name, cols.total_us, cols.total_inner_us, cols.count])

    def slow_iter(iterable):
        for x in iterable:
            time.sleep(0.1)
            yield x

    @func()
    def foo():
        time.sleep(0.02)
        with region('a'):
            time.sleep(0.02)
            for i in iter_proxy(slow_iter([0.1, 0.2, 0.3]), 'iter'):
                with region('b'):
                    time.sleep(i)

    with fresh_region_profiler(monkeypatch):
        install_profiler(reporter)
        foo()
        with region('x'):
            time.sleep(0.5)
        foo()

    expected = [[RegionProfiler.ROOT_NODE_NAME, 2380000, 0, '1'],
                ['foo()', 1880000, 40000, '2'],
                ['a', 1840000, 40000, '2'],
                ['b', 1200000, 1200000, '6'],
                ['iter', 600000, 600000, '6'],
                ['x', 500000, 500000, '1']]

    rows = reporter.rows[1:]
    lower = 0.99
    upper = 1.03
    upper_delta = 5000
    assert len(rows) == len(expected)
    print(rows)
    for i, (r, e) in enumerate(zip(rows, expected)):
        assert r[0] == e[0]
        assert r[3] == e[3]
        if i == 0:
            assert int(r[1]) > e[1]
        else:
            assert e[1] * lower <= int(r[1]) <= e[1] * upper + upper_delta
            assert e[2] * lower <= int(r[2]) <= e[2] * upper + upper_delta


