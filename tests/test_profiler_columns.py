import region_profiler.reporter_columns as cols
from region_profiler.reporters import Slice


def test_column_data():
    """Assert that column providers extract
    the correct data from the passed slice.
    """

    slices = [Slice(0, '<root>', None, 0, 1, 10, 1, 10, 10),
              Slice(1, 'a', None, 1, 3, 9, 5, 1, 4)]
    slices[1].parent = slices[0]
    s = slices[1]

    assert cols.count(s, slices) == '3'
    assert cols.name(s, slices) == 'a'
    assert cols.indented_name(s, slices) == '. a'
    assert cols.node_id(s, slices) == '1'
    assert cols.parent_id(s, slices) == '0'
    assert cols.parent_name(s, slices) == '<root>'
    assert cols.percents_of_total(s, slices) == '90.00%'
    assert cols.total(s, slices) == '9.000 s'
    assert cols.total_us(s, slices) == '9000000'
    assert cols.total_inner(s, slices) == '5.000 s'
    assert cols.total_inner_us(s, slices) == '5000000'
    assert cols.average(s, slices) == '3.000 s'
    assert cols.average_us(s, slices) == '3000000'
    assert cols.min(s, slices) == '1.000 s'
    assert cols.min_us(s, slices) == '1000000'
    assert cols.max(s, slices) == '4.000 s'
    assert cols.max_us(s, slices) == '4000000'
