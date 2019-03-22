import sys

import pytest

from region_profiler.profiler import RegionProfiler


@pytest.mark.parametrize('profiler_cls', [RegionProfiler])
@pytest.mark.parametrize('iter_cnt', [0, 1, 10])
def test_iter_proxy_proper_values(profiler_cls, iter_cnt):
    """Test that iter_proxy properly forwards iterable values.
    """
    rp = profiler_cls()

    l = list(range(iter_cnt))
    for i, x in enumerate(rp.iter_proxy(l, 'test_loop')):
        assert x == l[i]

    assert list(rp.root.children.keys()) == ['test_loop']
    n = rp.root.children['test_loop']
    assert list(n.children) == []
    assert n.stats.count == len(l)


def raise_after_n(n, err):
    for x in range(n):
        yield x
    raise err


@pytest.mark.parametrize('profiler_cls', [RegionProfiler])
@pytest.mark.parametrize('iter_cnt', [0, 1, 10])
def test_iter_proxy_custom_generator(profiler_cls, iter_cnt):
    """Test that iter_proxy properly forwards generator values.
    """
    if sys.version_info >= (3, 7):
        pytest.skip('It is not allowed to throw StopIteration from generator after Python 3.7')
    rp = profiler_cls()

    for _ in rp.iter_proxy(raise_after_n(iter_cnt, StopIteration), 'test_loop'):
        pass
    assert list(rp.root.children.keys()) == ['test_loop']
    n = rp.root.children['test_loop']
    assert list(n.children) == []
    assert n.stats.count == iter_cnt
    assert n.recursion_depth == 0  # check that timing is stopped


@pytest.mark.parametrize('profiler_cls', [RegionProfiler])
@pytest.mark.parametrize('iter_cnt', [0, 1, 10])
def test_iter_proxy_custom_exception(profiler_cls, iter_cnt):
    """Test that iter_proxy properly handles custom generator exceptions.
    """
    rp = profiler_cls()
    try:
        for _ in rp.iter_proxy(raise_after_n(iter_cnt, RuntimeError), 'test_loop'):
            pass
        assert False, "Should throw exception"
    except RuntimeError:
        pass

    assert list(rp.root.children.keys()) == ['test_loop']
    n = rp.root.children['test_loop']
    assert list(n.children) == []
    assert n.stats.count == iter_cnt + 1
    # iteration that throws custom exception is calculated
    assert n.recursion_depth == 0  # check that timing is stopped
