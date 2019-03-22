import time
from unittest import mock

import pytest

from region_profiler import RegionProfiler
from region_profiler.debug_listener import DebugListener


@pytest.mark.parametrize('profiler_cls', [RegionProfiler])
def test_recursive_global_func_call(profiler_cls):
    """Test that global functions are registered correctly.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = list(range(0, 100, 1))
    l = DebugListener()
    rp = profiler_cls(listeners=[l])

    @rp.func(asglobal=True)
    def foo(i):
        time.sleep(0.1)
        if i > 1:
            foo(i - 1)
        time.sleep(0.2)

    with rp.region('x'):
        foo(3)

    assert rp.current_node == rp.root
    assert rp.root.children['foo()'].stats.count == 1
    assert rp.root.children['foo()'].stats.total >= 0.9
    assert rp.root.children['foo()'].stats.total <= 0.92

    with rp.region('x'):
        foo(2)

    assert rp.current_node == rp.root
    assert rp.root.children['foo()'].stats.count == 2
    assert rp.root.children['foo()'].stats.total >= 1.5
    assert rp.root.children['foo()'].stats.total <= 1.55
