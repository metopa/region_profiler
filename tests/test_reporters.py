from region_profiler import RegionProfiler
from region_profiler.reporters import *


class FixedStats:
    def __init__(self, count, total, min, max):
        self.count = count
        self.total = total
        self.min = min
        self.max = max


def test_slice_generation():
    rp = RegionProfiler()

    with rp.region('a'):
        with rp.region('b'):
            pass

        for n in ['c', 'd']:
            with rp.region(n):
                with rp.region('x'):
                    pass

    rp.root.stats = FixedStats(1, 100, 100, 100)
    a = rp.root.children['a']
    a.stats = FixedStats(1, 90, 90, 90)
    a.children['b'].stats = FixedStats(4, 20, 2, 10)
    a.children['c'].stats = FixedStats(2, 30, 10, 20)
    a.children['c'].children['x'].stats = FixedStats(2, 10, 5, 5)
    a.children['d'].stats = FixedStats(1, 25, 25, 25)
    a.children['d'].children['x'].stats = FixedStats(1, 10, 10, 10)

    expected = [Slice(0, '<root>', None, 0, 1, 100, 10, 100, 100),
                Slice(1, 'a', None, 1, 1, 90, 15, 90, 90),
                Slice(2, 'c', None, 2, 2, 30, 20, 10, 20),
                Slice(3, 'x', None, 3, 2, 10, 10, 5, 5),
                Slice(4, 'd', None, 2, 1, 25, 15, 25, 25),
                Slice(5, 'x', None, 3, 1, 10, 10, 10, 10),
                Slice(6, 'b', None, 2, 4, 20, 20, 2, 10)
                ]
    expected[1].parent = expected[0]
    expected[2].parent = expected[1]
    expected[3].parent = expected[2]
    expected[4].parent = expected[1]
    expected[5].parent = expected[4]
    expected[6].parent = expected[1]

    slices = get_profiler_slice(rp)
    assert slices == expected


