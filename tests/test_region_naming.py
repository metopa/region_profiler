import pytest

from region_profiler.cython.profiler import \
    RegionProfiler as CythonRegionProfiler
from region_profiler.profiler import RegionProfiler


@pytest.mark.parametrize('profiler_cls', [RegionProfiler, CythonRegionProfiler])
def test_basic_naming(profiler_cls):
    """Test basic checkpoint naming works.
    """
    rp = profiler_cls()
    assert rp.root.children == {}

    with rp.region('a'):
        with rp.region('b'):
            pass

        for n in ['c', 'd']:
            with rp.region(n):
                with rp.region('x'):
                    pass

    children = rp.root.children
    assert set(children.keys()) == {'a'}
    assert children['a'].name == 'a'
    children = children['a'].children
    assert set(children.keys()) == {'b', 'c', 'd'}
    assert children['b'].children == {}
    assert set(children['c'].children.keys()) == {'x'}
    assert set(children['d'].children.keys()) == {'x'}
    assert children['c'].children['x'].children == {}
    assert children['d'].children['x'].children == {}


@pytest.mark.parametrize('profiler_cls', [RegionProfiler, CythonRegionProfiler])
def test_automatic_naming(profiler_cls):
    """Test that region name is correctly deduced from the code location.
    """
    rp = profiler_cls()

    def foo():
        with rp.region():
            pass

    with rp.region():
        foo()

    for _ in rp.iter_proxy([1, 2, 3]):
        pass

    r1 = 'test_automatic_naming() <test_region_naming.py:46>'
    r2 = 'foo() <test_region_naming.py:43>'
    r3 = 'test_automatic_naming() <test_region_naming.py:49>'
    assert sorted(list(rp.root.children.keys())) == sorted([r1, r3])
    assert rp.root.children[r1].name == r1
    assert rp.root.children[r3].name == r3
    assert list(rp.root.children[r1].children.keys()) == [r2]


@pytest.mark.parametrize('profiler_cls', [RegionProfiler, CythonRegionProfiler])
def test_func_decorator(profiler_cls):
    """Test that decorator properly wraps a function and
    have a proper name.
    """
    rp = profiler_cls()

    @rp.func('foo')
    def foo():
        with rp.region('inner'):
            return 42

    @rp.func('baz')
    def bar():
        return foo() + foo()

    x = bar() + foo()
    ch = rp.root.children
    assert set(ch.keys()) == {'foo()', 'baz()'}
    assert set(ch['foo()'].children.keys()) == {'inner'}
    assert set(ch['baz()'].children.keys()) == {'foo()'}
    assert set(ch['baz()'].children['foo()'].children.keys()) == {'inner'}


@pytest.mark.parametrize('profiler_cls', [RegionProfiler, CythonRegionProfiler])
def test_func_automatic_naming(profiler_cls):
    """Test that decorated region name is correctly
    deduced from the code location.
    """
    rp = profiler_cls()

    @rp.func()
    def foo():
        with rp.region('inner'):
            return 42

    @rp.func()
    def baz():
        return foo() + foo()

    x = baz() + foo()
    ch = rp.root.children
    assert set(ch.keys()) == {'foo()', 'baz()'}
    assert set(ch['foo()'].children.keys()) == {'inner'}
    assert set(ch['baz()'].children.keys()) == {'foo()'}
    assert set(ch['baz()'].children['foo()'].children.keys()) == {'inner'}


@pytest.mark.parametrize('profiler_cls', [RegionProfiler, CythonRegionProfiler])
def test_global_regions(profiler_cls):
    """Test that regions marked as global has root as a parent.
    """
    rp = profiler_cls()

    @rp.func('foo', asglobal=True)
    def foo():
        with rp.region('inner', asglobal=True):
            return sum(rp.iter_proxy([1, 2, 3], name='sum', asglobal=True))

    @rp.func('baz')
    def bar():
        with rp.region('plus'):
            return foo() + foo()

    x = bar() + foo()
    ch = rp.root.children
    assert set(ch.keys()) == {'foo()', 'baz()', 'inner', 'sum'}
    assert len(ch['foo()'].children.keys()) == 0
    assert set(ch['baz()'].children.keys()) == {'plus'}
    assert len(ch['baz()'].children['plus'].children.keys()) == 0
    assert len(ch['foo()'].children.keys()) == 0
    assert len(ch['inner'].children.keys()) == 0
    assert len(ch['sum'].children.keys()) == 0
