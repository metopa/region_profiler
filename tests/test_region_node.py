import time
from unittest import mock

import pytest

from region_profiler.node import RegionNode, RootNode
from region_profiler.utils import SeqStats, Timer


@pytest.mark.parametrize('node_cls', [RegionNode])
def test_base_attributes(node_cls):
    """Assert that RegionNode exposes basic attributes.
    """
    t1 = lambda: None  # mock timer
    n = node_cls('node', timer_cls=t1)
    assert n.name == 'node'
    assert n.timer_cls == t1
    assert n.stats == SeqStats()


@pytest.mark.parametrize('node_cls,child_node_cls,timer_cls',
                         [(RegionNode, RegionNode, Timer),
                          (RootNode, RegionNode, Timer)])
def test_children(node_cls, child_node_cls, timer_cls):
    """Test that RegionNode properly creates its children upon request.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 20]
    t1_cls = lambda: timer_cls(clock=mock_clock)
    t2_cls = lambda: timer_cls(clock=mock_clock)

    n = node_cls(name='0', timer_cls=t1_cls)
    ch1 = n.get_child('1')
    ch2 = n.get_child('2', timer_cls=t2_cls)

    assert n.get_child('1') == ch1
    assert isinstance(ch1, child_node_cls)
    assert ch1.name == '1'
    assert ch1.timer_cls == t1_cls

    assert isinstance(ch2, child_node_cls)
    assert n.get_child('2') == ch2
    assert ch2.name == '2'
    assert ch2.timer_cls == t2_cls


@pytest.mark.parametrize('node_cls,timer_cls',
                         [(RegionNode, Timer)])
def test_timing(node_cls, timer_cls):
    """Test that RegionNode correctly reacts on enter/exit events.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 20]
    t_cls = lambda: timer_cls(clock=mock_clock)

    n = node_cls('x', timer_cls=t_cls)
    assert n.stats == SeqStats()
    n.enter_region()
    assert n.stats == SeqStats()
    n.exit_region()
    assert n.stats == SeqStats(count=1, total=10, min=10, max=10)


@pytest.mark.parametrize('node_cls,timer_cls',
                         [(RegionNode, Timer)])
def test_multiple_timing(node_cls, timer_cls):
    """Test that RegionNode correctly calculates multiple enter events.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 20, 33, 40, 50, 70]
    t_cls = lambda: timer_cls(clock=mock_clock)

    n = node_cls('x', timer_cls=t_cls)
    n.enter_region()
    n.exit_region()
    n.enter_region()
    n.exit_region()
    assert n.stats == SeqStats(count=2, total=17, min=7, max=10)
    n.enter_region()
    n.exit_region()
    assert n.stats == SeqStats(count=3, total=37, min=7, max=20)


@pytest.mark.parametrize('node_cls', [RegionNode])
def test_timing_with_real_clock(node_cls):
    """Test that RegionNode uses real clock by default.
    """
    n = node_cls('x')
    n.enter_region()
    time.sleep(1)
    n.exit_region()
    dur = n.stats.total
    assert 1 <= dur <= 1.01
    assert n.stats == SeqStats(count=1, total=dur, min=dur, max=dur)


@pytest.mark.parametrize('node_cls', [RegionNode])
def test_str_conversion(node_cls):
    """Test __str__ and __repr__ methods.
    """
    n = node_cls('node', timer_cls=lambda: None)
    assert str(n) == 'node'
    assert isinstance(repr(n), str)


@pytest.mark.parametrize('node_cls,timer_cls', [(RegionNode, Timer)])
def test_cancellation(node_cls, timer_cls):
    """Test timing cancellation event.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [5, 7, 10, 20, 21, 22]
    t_cls = lambda: timer_cls(clock=mock_clock)

    n = node_cls('x', timer_cls=t_cls)
    n.enter_region()
    n.cancel_region()
    n.enter_region()
    n.exit_region()
    assert n.stats == SeqStats(count=1, total=10, min=10, max=10)
    n.enter_region()
    n.cancel_region()
    assert n.stats == SeqStats(count=1, total=10, min=10, max=10)


@pytest.mark.parametrize('node_cls,timer_cls', [(RootNode, Timer)])
def test_root_stats(node_cls, timer_cls):
    """Test that RootNode has special handling for stats property.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [5, 11, 11, 11]
    t_cls = lambda: timer_cls(clock=mock_clock)

    n = node_cls(timer_cls=t_cls)
    assert n.stats.count == 1
    assert n.stats.total == 6
    assert n.stats.min == 6
    assert n.stats.max == 6


@pytest.mark.parametrize('node_cls,timer_cls', [(RootNode, Timer)])
def test_root_cancellation(node_cls, timer_cls):
    """Test that RootNode raises a warning on cancellation event.
    """
    with pytest.warns(UserWarning):
        mock_clock = mock.Mock()
        mock_clock.side_effect = [5, 11, 11, 11]
        t_cls = lambda: timer_cls(clock=mock_clock)

        n = node_cls(timer_cls=t_cls)
        n.cancel_region()
