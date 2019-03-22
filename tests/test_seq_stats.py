import pytest

from region_profiler.utils import SeqStats


@pytest.mark.parametrize('stats_cls', [SeqStats])
def test_seq_stats(stats_cls):
    values = [5, 44, 6, 3, 7]

    s = stats_cls()
    assert s.count == 0
    assert s.total == 0
    assert s.avg == 0
    assert s.min == 0
    assert s.max == 0

    s.add(values[0])
    assert s.count == 1
    assert s.total == values[0]
    assert s.avg == values[0]
    assert s.min == values[0]
    assert s.max == values[0]

    for v in values[1:]:
        s.add(v)

    assert s.count == len(values)
    assert s.total == sum(values)
    assert s.avg == sum(values) / len(values)
    assert s.min == min(values)
    assert s.max == max(values)
