import json
import os
import threading
from unittest import mock

from region_profiler import RegionProfiler
from region_profiler.chrome_trace_listener import ChromeTraceListener
from region_profiler.utils import Timer


def test_chrome_trace(tmpdir, capsys):
    """Test that ChromeTraceListener generates a correct trace on regular usage.
    """
    trace_file = tmpdir.join('trace.json')
    mock_clock = mock.Mock()
    mock_clock.side_effect = list(range(0, 100, 1))
    rp = RegionProfiler(listeners=[ChromeTraceListener(str(trace_file))],
                        timer_cls=lambda: Timer(mock_clock))

    with rp.region('a'):
        for _ in [1, 2, 3]:
            with rp.region('b'):
                pass

    rp.finalize()

    pid = os.getpid()
    tid = threading.get_ident()
    expected = [
        {'name': rp.ROOT_NODE_NAME, 'ph': 'B', 'ts': 0, 'pid': pid, 'tid': tid},
        {'name': 'a', 'ph': 'B', 'ts': 1000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'B', 'ts': 2000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'E', 'ts': 3000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'B', 'ts': 4000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'E', 'ts': 5000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'B', 'ts': 6000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'E', 'ts': 7000000, 'pid': pid, 'tid': tid},
        {'name': 'a', 'ph': 'E', 'ts': 8000000, 'pid': pid, 'tid': tid},
        {'name': rp.ROOT_NODE_NAME, 'ph': 'E', 'ts': 9000000, 'pid': pid, 'tid': tid},
    ]

    assert os.path.isfile(str(trace_file))
    with trace_file.open() as f:
        trace = json.load(f)
    assert trace[2:] == expected


def test_chrome_trace_node_canceled(tmpdir, capsys):
    """Assert that ChromeTraceListener doesn't
    generate records for canceled nodes,
    that occurs during the last iteration.
    """
    trace_file = tmpdir.join('trace.json')
    mock_clock = mock.Mock()
    mock_clock.side_effect = list(range(0, 100, 1))
    rp = RegionProfiler(listeners=[ChromeTraceListener(str(trace_file))],
                        timer_cls=lambda: Timer(mock_clock))

    with rp.region('a'):
        for _ in rp.iter_proxy([1, 2], 'b'):
            with rp.region('c'):
                pass

    rp.finalize()

    pid = os.getpid()
    tid = threading.get_ident()
    expected = [
        {'name': rp.ROOT_NODE_NAME, 'ph': 'B', 'ts': 0, 'pid': pid, 'tid': tid},
        {'name': 'a', 'ph': 'B', 'ts': 1000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'B', 'ts': 2000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'E', 'ts': 3000000, 'pid': pid, 'tid': tid},
        {'name': 'c', 'ph': 'B', 'ts': 4000000, 'pid': pid, 'tid': tid},
        {'name': 'c', 'ph': 'E', 'ts': 5000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'B', 'ts': 6000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'E', 'ts': 7000000, 'pid': pid, 'tid': tid},
        {'name': 'c', 'ph': 'B', 'ts': 8000000, 'pid': pid, 'tid': tid},
        {'name': 'c', 'ph': 'E', 'ts': 9000000, 'pid': pid, 'tid': tid},
        {'name': 'a', 'ph': 'E', 'ts': 12000000, 'pid': pid, 'tid': tid},
        {'name': rp.ROOT_NODE_NAME, 'ph': 'E', 'ts': 13000000, 'pid': pid, 'tid': tid},
    ]

    assert os.path.isfile(str(trace_file))
    with trace_file.open() as f:
        trace = json.load(f)
    assert trace[2:] == expected


def test_chrome_trace_parent_node_canceled(tmpdir, capsys):
    """Assert that ChromeTraceListener still
    generates records for canceled nodes,
    if its child has been accessed.
    """
    trace_file = tmpdir.join('trace.json')
    mock_clock = mock.Mock()
    mock_clock.side_effect = list(range(0, 100, 1))
    rp = RegionProfiler(listeners=[ChromeTraceListener(str(trace_file))],
                        timer_cls=lambda: Timer(mock_clock))

    def iter_with_region(iterable):
        for i in iterable:
            with rp.region('d'):
                pass
            yield i
        with rp.region('exit'):
            pass

    with rp.region('a'):
        for _ in rp.iter_proxy(iter_with_region([1, 2]), 'b'):
            with rp.region('c'):
                pass

    rp.finalize()

    pid = os.getpid()
    tid = threading.get_ident()
    expected = [
        {'name': rp.ROOT_NODE_NAME, 'ph': 'B', 'ts': 0, 'pid': pid, 'tid': tid},
        {'name': 'a', 'ph': 'B', 'ts': 1000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'B', 'ts': 2000000, 'pid': pid, 'tid': tid},
        {'name': 'd', 'ph': 'B', 'ts': 3000000, 'pid': pid, 'tid': tid},
        {'name': 'd', 'ph': 'E', 'ts': 4000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'E', 'ts': 5000000, 'pid': pid, 'tid': tid},
        {'name': 'c', 'ph': 'B', 'ts': 6000000, 'pid': pid, 'tid': tid},
        {'name': 'c', 'ph': 'E', 'ts': 7000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'B', 'ts': 8000000, 'pid': pid, 'tid': tid},
        {'name': 'd', 'ph': 'B', 'ts': 9000000, 'pid': pid, 'tid': tid},
        {'name': 'd', 'ph': 'E', 'ts': 10000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'E', 'ts': 11000000, 'pid': pid, 'tid': tid},
        {'name': 'c', 'ph': 'B', 'ts': 12000000, 'pid': pid, 'tid': tid},
        {'name': 'c', 'ph': 'E', 'ts': 13000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'B', 'ts': 14000000, 'pid': pid, 'tid': tid},
        {'name': 'exit', 'ph': 'B', 'ts': 15000000, 'pid': pid, 'tid': tid},
        {'name': 'exit', 'ph': 'E', 'ts': 16000000, 'pid': pid, 'tid': tid},
        {'name': 'b', 'ph': 'E', 'ts': 17000000, 'pid': pid, 'tid': tid},
        {'name': 'a', 'ph': 'E', 'ts': 18000000, 'pid': pid, 'tid': tid},
        {'name': rp.ROOT_NODE_NAME, 'ph': 'E', 'ts': 19000000, 'pid': pid, 'tid': tid},
    ]

    assert os.path.isfile(str(trace_file))
    with trace_file.open() as f:
        trace = json.load(f)
    assert trace[2:] == expected
