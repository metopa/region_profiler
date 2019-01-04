import sys

from region_profiler import reporter_columns as cols


class Slice:
    """:py:class:`Slice` is an entry in
    a serialized list of :py:class:`region_profiler.node.RegionNode`.

    When a profiler report is generated,
    a slice of the current profiler data is taken
    (using :py:func:`get_node_slice`).
    Each entry in this slice is an instance of :py:class:`Slice`,
    that contains all data about a corresponding node,
    that may be useful for reporting. Data from a slice
    is not accessed directly, but using column providers,
    defined in :py:mod:`region_profiler.reporter_columns`.

    Attributes:
        id(int): unique slice id
        name(str): node name
        parent(:py:class:`Slice`, optional): parent node in the hierarchy
        call_depth(int): node depth in the hierarchy
        count(int): number of region hits
        total_time(float): total time spent in the corresponding region
        total_inner_time(float): total time spent in the corresponding region
                                 minus total time of all node ancestors
        min_time(float): minimal duration, spent in the corresponding region
        max_time(float): maximal duration, spent in the corresponding region
    """

    def __init__(self, id, name, parent, call_depth, count,
                 total_time, total_inner_time, min_time, max_time):
        """
        Args:
            id(int): unique slice id
            name(str): node name
            parent(:py:class:`Slice`): parent node in the hierarchy
            call_depth(int): node depth in the hierarchy
            count(int): number of region hits
            total_time(float): total time spent in the corresponding region
            total_inner_time(float): total time spent in the corresponding region
                                     minus total time of all node descendants
            min_time(float): minimal duration, spent in the corresponding region
            max_time(float): maximal duration, spent in the corresponding region
        """
        self.id = id
        self.name = name
        self.parent = parent
        self.call_depth = call_depth
        self.count = count
        self.total_time = total_time
        self.total_inner_time = total_inner_time
        self.avg_time = total_time / count if count else 0
        self.min_time = min_time
        self.max_time = max_time

    @property
    def parent_name(self):
        """Convenience method for retrieving parent node name.
        """
        return self.parent.name if self.parent else ''

    def __str__(self):
        return 'Slice({})'.format(', '.join(
            '{}={}'.format(k, getattr(self, k)) for k in
            ('id', 'name', 'parent_name', 'call_depth',
             'count', 'total_time', 'total_inner_time',
             'min_time', 'max_time')
        ))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return all(getattr(self, n) == getattr(other, n) for n in
                   ('id', 'name', 'parent_name', 'call_depth', 'count',
                    'total_time', 'total_inner_time', 'min_time', 'max_time'))


def get_node_slice(slices, node, parent_slice, call_depth):
    """Serialize a node and its descendants data in a list of :py:class:`Slice`.

    Descendants are serialized sorted by their total time in decreasing order.

    Args:
        slices (list of :py:class:`Slice`): global list of slices
        node (:py:class:`region_profiler.node.RegionNode`): current node that is to be serialized
        parent_slice (:py:class:`Slice`, optional): link to a slice of the parent node
        call_depth (int): depth of the node in the hierarchy
    """
    s = Slice(len(slices), node.name, parent_slice, call_depth, node.stats.count,
              node.stats.total, 0, node.stats.min, node.stats.max)
    slices.append(s)

    child_total = 0

    for ch in sorted(node.children.values(), key=lambda n: -n.stats.total):
        get_node_slice(slices, ch, s, call_depth + 1)
        child_total += ch.stats.total

    s.total_inner_time = max(s.total_time - child_total, 0)


def get_profiler_slice(rp):
    """Serialize a profiler state in a list of :py:class:`Slice`.

    Descendants are serialized sorted by their total time in decreasing order.

    Args:
        rp(:py:class:`region_profiler.profiler.RegionProfiler`): profiler

    Returns:
        list of :py:class:`Slice`: serialized nodes of the profiler
    """
    slices = []
    get_node_slice(slices, rp.root, None, 0)
    return slices


DEFAULT_CONSOLE_COLUMNS = (cols.indented_name, cols.total,
                           cols.percents_of_total, cols.count,
                           cols.min, cols.average, cols.max)
"""Default column list for :py:class:`ConsoleReporter`.
"""


class ConsoleReporter:
    """Print profiler state in a human-readable way to console.

    Data is printed in a table with a configurable set of columns
    (default columns: name, total duration, % of total,
    hit count, min, average, max).

    Nodes are printed in a depth-first order with siblings processed
    sorted by the total time descending.

    By default, these column are reported:

    - name
    - total time inside region
    - percents of total application time
    - number of timer region was hit
    - min time inside region
    - average time inside region
    - max time inside region

    Example output::

        name                           total  % of total  count       min   average       max
        --------------------------  --------  ----------  -----  --------  --------  --------
        <root>                        925 ms     100.00%      1    925 ms    925 ms    925 ms
        . bar()                     494.5 ms      53.48%      1  494.5 ms  494.5 ms  494.5 ms
        . . loop                    408.1 ms      44.14%      1  408.1 ms  408.1 ms  408.1 ms
        . . . iter                  400.9 ms      43.36%      4  100.2 ms  100.2 ms  100.2 ms
        . . init                    12.85 ms       1.39%      2  5.776 ms  6.426 ms  7.076 ms
        . . bar() <example2.py:40>  7.866 ms       0.85%      1  7.866 ms  7.866 ms  7.866 ms
    """

    def __init__(self, columns=DEFAULT_CONSOLE_COLUMNS, stream=sys.stderr):
        """Initialize the reporter.

        Args:
            columns(list of report columns): list of columns that are used in the printout.
            stream (file-like object): stream for output
        """
        self.columns = columns
        self.stream = stream

    def dump_profiler(self, rp):
        """Dump the profiler state.

        Args:
            rp(:py:class:`region_profiler.profiler.RegionProfiler`): region profiler
        """
        slices = get_profiler_slice(rp)

        rows = [[col.column_print_name for col in self.columns]]
        col_width = [len(n) for n in rows[0]]

        for s in slices:
            row = [col(s, slices) for col in self.columns]
            rows.append(row)
            for i, c in enumerate(row):
                col_width[i] = max(col_width[i], len(c))
        rows.insert(1, ['-' * w for w in col_width])
        delim = '  '
        format = delim.join('{:' + ('<' if i == 0 else '>') + str(w) + '}' for i, w in enumerate(col_width))
        sys.stdout.flush()
        for r in rows:
            print(format.format(*r), file=self.stream)


DEFAULT_CSV_COLUMNS = (cols.node_id, cols.name, cols.parent_id, cols.parent_name,
                       cols.total_us, cols.total_inner_us,
                       cols.count, cols.min_us, cols.average_us, cols.max_us)
"""Default column list for :py:class:`CsvReporter`.
"""


class CsvReporter:
    """Print profiler state in a CSV format.

    Data is printed in a table with a configurable set of columns
    (default columns: id, name, parent_id, parent_name, total_us,
    total_inner_us, count, min_us, average_us, max_us).

    Nodes are printed in a depth-first order with siblings processed
    sorted by the total time descending.

    By default, these column are reported:

    - id
    - name
    - parent node id
    - parent node name
    - total time inside region in us
    - total time inside region in us excluding time inside its child regions
    - number of timer region was hit
    - min time inside region in us
    - average time inside region in us
    - max time inside region in us

    Example output::

        id, name, parent_id, parent_name, total_us, total_inner_us, count, min_us, average_us, max_us
        0, <root>, , , 966221, 443352, 1, 966221, 966221, 966221
        1, bar(), 0, <root>, 522868, 68080, 1, 522868, 522868, 522868
        2, loop, 1, bar(), 410395, 9517, 1, 410395, 410395, 410395
        3, iter, 2, loop, 400877, 400877, 4, 100208, 100219, 100227
        4, init, 1, bar(), 35456, 35456, 2, 16589, 17728, 18867
        5, bar() <example2.py:42>, 1, bar(), 8935, 8935, 1, 8935, 8935, 8935

    """

    def __init__(self, columns=DEFAULT_CSV_COLUMNS, stream=sys.stderr):
        """Initialize the reporter.

        Args:
            columns(list of report columns): list of columns that are used in the printout.
            stream (file-like object): stream for output
        """
        self.columns = columns
        self.stream = stream

    def dump_profiler(self, rp):
        """Dump the profiler state.

        Args:
            rp(:py:class:`region_profiler.profiler.RegionProfiler`): region profiler
        """
        slices = get_profiler_slice(rp)

        rows = [[col.column_name for col in self.columns]]

        for s in slices:
            row = [col(s, slices) for col in self.columns]
            rows.append(row)

        for r in rows:
            print(', '.join(r), file=self.stream)


class SilentReporter:
    """Dummy test reporter. It stores rows in its attribute ``rows``.

    Nodes are printed in a depth-first order with siblings processed
    sorted by the total time descending.
    """

    def __init__(self, columns):
        """Initialize the reporter.

        Args:
            columns(list of report columns): list of columns that are collected.
        """
        self.columns = columns
        self.rows = None

    def dump_profiler(self, rp):
        """Dump the profiler state.

        Args:
            rp(:py:class:`region_profiler.profiler.RegionProfiler`): region profiler
        """
        slices = get_profiler_slice(rp)

        rows = [[col.column_name for col in self.columns]]

        for s in slices:
            row = [col(s, slices) for col in self.columns]
            rows.append(row)

        self.rows = rows
