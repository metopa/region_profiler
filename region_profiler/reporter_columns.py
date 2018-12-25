"""Define columns that may be used for configuring reporters
(see :py:mod:`region_profiler.reporter_columns`).

Each column is defined as a function, that takes a current
:py:class:`region_profiler.reporter_columns.Slice` and a list
of all slices and returns the requested metrics of the current slice.

Each column stores its name in ``column_name`` attribute.
"""

from region_profiler.utils import pretty_print_time


def as_column(name=None):
    """Mark a function as a column provider.

    Args:
        name (:obj:`str`, optional): column name. If None, function name is used
    """
    def decorate(func):
        setattr(func, 'column_name', name or func.__name__)
        return func
    return decorate


@as_column()
def name(this_slice, all_slices):
    return this_slice.name


@as_column('name')
def indented_name(this_slice, all_slices):
    return '. ' * this_slice.call_depth + this_slice.name


@as_column('id')
def node_id(this_slice, all_slices):
    return str(this_slice.id)


@as_column('parent_id')
def parent_id(this_slice, all_slices):
    return str(this_slice.parent.id) if this_slice.parent else ''


@as_column('parent_name')
def parent_name(this_slice, all_slices):
    return this_slice.parent.name if this_slice.parent else ''


@as_column('% of total')
def percents_of_total(this_slice, all_slices):
    p = this_slice.total_time * 100. / all_slices[0].total_time
    return '{:.2f}%'.format(p)


@as_column()
def count(this_slice, all_slices):
    return str(this_slice.count)


@as_column()
def total_us(this_slice, all_slices):
    return str(int(this_slice.total_time * 1000000))


@as_column()
def total(this_slice, all_slices):
    return pretty_print_time(this_slice.total_time)


@as_column()
def total_inner_us(this_slice, all_slices):
    return str(int(this_slice.total_inner_time * 1000000))


@as_column()
def total_inner(this_slice, all_slices):
    return pretty_print_time(this_slice.total_inner_time)


@as_column()
def average_us(this_slice, all_slices):
    return str(int(this_slice.avg_time * 1000000))


@as_column()
def average(this_slice, all_slices):
    return pretty_print_time(this_slice.avg_time)


@as_column()
def min_us(this_slice, all_slices):
    return str(int(this_slice.min_time * 1000000))


@as_column()
def min(this_slice, all_slices):
    return pretty_print_time(this_slice.min_time)


@as_column()
def max_us(this_slice, all_slices):
    return str(int(this_slice.max_time * 1000000))


@as_column()
def max(this_slice, all_slices):
    return pretty_print_time(this_slice.max_time)
