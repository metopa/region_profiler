import time
from unittest import mock

import pytest

from region_profiler import Timer
from region_profiler.node import RegionNode, RootNode
from region_profiler.utils import SeqStats


def test_base_attributes():
    """Assert that RegionNode exposes basic attributes.
    """
    t1 = object()  # mock timer
    n = RegionNode('node', timer_cls=t1)
    assert n.name == 'node'
    assert n.timer_cls == t1
    assert n.stats == SeqStats()


@pytest.mark.parametrize("node_class", [RegionNode, RootNode])
def test_children(node_class):
    """Test that RegionNode properly creates its children upon request.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 20]
    t1_cls = lambda: Timer(clock=mock_clock)
    t2_cls = lambda: Timer(clock=mock_clock)

    n = node_class(name='0', timer_cls=t1_cls)
    ch1 = n.get_child('1')
    ch2 = n.get_child('2', timer_cls=t2_cls)

    assert n.get_child('1') == ch1
    assert isinstance(ch1, RegionNode)
    assert ch1.name == '1'
    assert ch1.timer_cls == t1_cls

    assert isinstance(ch2, RegionNode)
    assert n.get_child('2') == ch2
    assert ch2.name == '2'
    assert ch2.timer_cls == t2_cls


def test_timing():
    """Test that RegionNode correctly reacts on enter/exit events.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 20]
    t_cls = lambda: Timer(clock=mock_clock)

    n = RegionNode('x', timer_cls=t_cls)
    assert n.stats == SeqStats()
    n.enter_region()
    assert n.stats == SeqStats()
    n.exit_region()
    assert n.stats == SeqStats(count=1, total=10, min=10, max=10)
    n.exit_region()
    assert n.stats == SeqStats(count=1, total=10, min=10, max=10)


def test_multiple_timing():
    """Test that RegionNode correctly calculates multiple enter events.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [10, 20, 33, 40, 50, 70]
    t_cls = lambda: Timer(clock=mock_clock)

    n = RegionNode('x', timer_cls=t_cls)
    n.enter_region()
    n.exit_region()
    n.enter_region()
    n.exit_region()
    assert n.stats == SeqStats(count=2, total=17, min=7, max=10)
    n.enter_region()
    n.exit_region()
    assert n.stats == SeqStats(count=3, total=37, min=7, max=20)


def test_timing_with_real_clock():
    """Test that RegionNode uses real clock by default.
    """
    n = RegionNode('x')
    n.enter_region()
    time.sleep(1)
    n.exit_region()
    dur = n.stats.total
    assert 1 <= dur <= 1.01
    assert n.stats == SeqStats(count=1, total=dur, min=dur, max=dur)


def test_str_conversion():
    """Test __str__ and __repr__ methods.
    """
    n = RegionNode('node', timer_cls='__timer_cls__')
    assert str(n) == 'node'
    assert repr(n) == ('RegionNode(name="node", '
                       'stats=SeqStats(count=0, total=0, min=0, max=0), '
                       'timer_cls=__timer_cls__)')


def test_cancellation():
    """Test timing cancellation event.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [5, 10, 20, 21]
    t_cls = lambda: Timer(clock=mock_clock)

    n = RegionNode('x', timer_cls=t_cls)
    n.enter_region()
    n.cancel_region()
    n.enter_region()
    n.exit_region()
    assert n.stats == SeqStats(count=1, total=10, min=10, max=10)
    n.enter_region()
    n.cancel_region()
    assert n.stats == SeqStats(count=1, total=10, min=10, max=10)


def test_root_stats():
    """Test that RootNode has special handling for stats property.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [5, 11, 11, 11]
    t_cls = lambda: Timer(clock=mock_clock)

    n = RootNode(timer_cls=t_cls)
    assert n.stats.count == 1
    assert n.stats.total == 6
    assert n.stats.min == 6
    assert n.stats.max == 6


def test_root_cancellation():
    """Test that RootNode raises a warning on cancellation event.
    """
    with pytest.warns(UserWarning):
        mock_clock = mock.Mock()
        mock_clock.side_effect = [5, 11, 11, 11]
        t_cls = lambda: Timer(clock=mock_clock)

        n = RootNode(timer_cls=t_cls)
        n.cancel_region()


def test_root_restart():
    """Test that RootNode continues previous timing on restart.
    """
    mock_clock = mock.Mock()
    mock_clock.side_effect = [5, 11, 20, 23, 23, 23]
    t_cls = lambda: Timer(clock=mock_clock)

    n = RootNode(timer_cls=t_cls)
    n.exit_region()
    assert n.stats.count == 1
    assert n.stats.total == 6
    assert n.stats.min == 6
    assert n.stats.max == 6
    n.enter_region()
    assert n.stats.count == 1
    assert n.stats.total == 9
    assert n.stats.min == 9
    assert n.stats.max == 9

