import pytest

from region_profiler import RegionProfiler
from region_profiler import reporter_columns as cols
from region_profiler.reporters import *


class FixedStats:
    def __init__(self, count, total, min, max):
        self.count = count
        self.total = total
        self.min = min
        self.max = max


@pytest.fixture()
def dummy_region_profiler():
    """Generate dummy region profiler to test reporters.
    """
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

    return rp


def test_slice_generation(dummy_region_profiler):
    """Test that node tree is properly serialized in a list.
    """
    expected = [Slice(0, RegionProfiler.ROOT_NODE_NAME, None, 0, 1, 100, 10, 100, 100),
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

    slices = get_profiler_slice(dummy_region_profiler)
    assert slices == expected


def test_silent_reporter(dummy_region_profiler):
    """Test :py:class:`SilentReporter` reporter.
    """
    r = SilentReporter([cols.name, cols.node_id, cols.parent_id, cols.total_us])

    r.dump_profiler(dummy_region_profiler)

    expected = [['name', 'id', 'parent_id', 'total_us'],
                [RegionProfiler.ROOT_NODE_NAME, '0', '', '100000000'],
                ['a', '1', '0', '90000000'],
                ['c', '2', '1', '30000000'],
                ['x', '3', '2', '10000000'],
                ['d', '4', '1', '25000000'],
                ['x', '5', '4', '10000000'],
                ['b', '6', '1', '20000000']]

    assert r.rows == expected


def test_console_reporter(dummy_region_profiler, capsys):
    """Test :py:class:`ConsoleReporter` reporter.
    """
    r = ConsoleReporter([cols.name, cols.node_id, cols.parent_id, cols.total_us],
                        stream=sys.stdout)

    r.dump_profiler(dummy_region_profiler)

    expected = [['name', 'id', 'parent id', 'total us'],
                [],
                [RegionProfiler.ROOT_NODE_NAME, '0', '', '100000000'],
                ['a', '1', '0', '90000000'],
                ['c', '2', '1', '30000000'],
                ['x', '3', '2', '10000000'],
                ['d', '4', '1', '25000000'],
                ['x', '5', '4', '10000000'],
                ['b', '6', '1', '20000000']]

    output, err = capsys.readouterr()
    output = output.strip().split('\n')
    assert len(output) == len(expected)

    for row, expected_vals in zip(output, expected):
        assert len(row) == len(output[0])
        for v in expected_vals:
            assert v in row


def test_csv_reporter(dummy_region_profiler, capsys):
    """Test :py:class:`CsvReporter` reporter.
    """
    r = CsvReporter([cols.name, cols.node_id, cols.parent_id, cols.total_us],
                    stream=sys.stdout)

    r.dump_profiler(dummy_region_profiler)

    expected = [['name', 'id', 'parent_id', 'total_us'],
                [RegionProfiler.ROOT_NODE_NAME, '0', '', '100000000'],
                ['a', '1', '0', '90000000'],
                ['c', '2', '1', '30000000'],
                ['x', '3', '2', '10000000'],
                ['d', '4', '1', '25000000'],
                ['x', '5', '4', '10000000'],
                ['b', '6', '1', '20000000']]

    output, err = capsys.readouterr()
    output = [[c.strip() for c in r.split(',')] for r in output.strip().split('\n')]

    assert len(output) == len(expected)
    for row, expected_vals in zip(output, expected):
        assert len(row) == len(expected_vals)
        for col, v in zip(row, expected_vals):
            assert col == v
