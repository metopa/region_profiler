from region_profiler.profiler import RegionProfiler


def test_basic_naming():
    """Test basic checkpoint naming is kept.
    """
    rp = RegionProfiler()
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


def test_automatic_naming():
    """Test that region name is correctly deduced from the code location.
    """

    def foo():
        with rp.region():
            pass

    rp = RegionProfiler()

    with rp.region():
        foo()
    r1 = 'test_automatic_naming <test_region_naming.py:41>'
    r2 = 'foo <test_region_naming.py:36>'
    assert list(rp.root.children.keys()) == [r1]
    assert rp.root.children[r1].name == r1
    assert list(rp.root.children[r1].children.keys()) == [r2]


def test_func_decorator():
    """Test that decorator properly wraps a function and
    have a proper name.
    """
    rp = RegionProfiler()

    @rp.func('foo')
    def foo():
        with rp.region('inner'):
            return 42

    @rp.func('baz')
    def bar():
        return foo() + foo()

    x = bar() + foo()
    ch = rp.root.children
    assert set(ch.keys()) == {'foo', 'baz'}
    assert set(ch['foo'].children.keys()) == {'inner'}
    assert set(ch['baz'].children.keys()) == {'foo'}
    assert set(ch['baz'].children['foo'].children.keys()) == {'inner'}


def test_func_automatic_naming():
    """Test that decorated region name is correctly
    deduced from the code location.
    """
    rp = RegionProfiler()

    @rp.func()
    def foo():
        with rp.region('inner'):
            return 42

    @rp.func()
    def baz():
        return foo() + foo()

    x = baz() + foo()
    ch = rp.root.children
    assert set(ch.keys()) == {'foo', 'baz'}
    assert set(ch['foo'].children.keys()) == {'inner'}
    assert set(ch['baz'].children.keys()) == {'foo'}
    assert set(ch['baz'].children['foo'].children.keys()) == {'inner'}
