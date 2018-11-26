from region_profiler.region_profiler import RegionProfiler


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
    def foo():
        with rp.region():
            pass

    rp = RegionProfiler()

    with rp.region():
        foo()
    cp1 = 'test_automatic_naming <test_region_naming.py:38>'
    cp2 = 'foo <test_region_naming.py:33>'
    assert list(rp.root.children.keys()) == [cp1]
    assert rp.root.children[cp1].name == cp1
    assert list(rp.root.children[cp1].children.keys()) == [cp2]
