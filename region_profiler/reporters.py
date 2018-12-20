import sys

from region_profiler import reporter_columns as cols


class Slice:
    def __init__(self, id, name, parent, call_depth, count,
                 total_time, total_inner_time, min_time, max_time):
        self.id = id
        self.name = name
        self.parent = parent
        self.call_depth = call_depth
        self.count = count
        self.total_time = total_time
        self.total_inner_time = total_inner_time
        self.avg_time = total_time / count
        self.min_time = min_time
        self.max_time = max_time

    @property
    def parent_name(self):
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
    """

    Args:
        slices (list):
        node (region_profiler.node.RegionNode):
        parent_slice (Slice, optional):
        call_depth (int):
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
    slices = []
    get_node_slice(slices, rp.root, None, 0)
    return slices


DEFAULT_CONSOLE_COLUMNS = (cols.indented_name, cols.total,
                           cols.percent_of_whole, cols.count,
                           cols.min, cols.average, cols.max)


class ConsoleReporter:
    def __init__(self, columns=DEFAULT_CONSOLE_COLUMNS, stream=sys.stderr):
        self.columns = columns
        self.stream = stream

    def print_summary(self, rp):
        slices = get_profiler_slice(rp)

        rows = [[col.column_name for col in self.columns]]
        col_width = [len(n) for n in rows[0]]

        for s in slices:
            row = [col(s, slices) for col in self.columns]
            rows.append(row)
            for i, c in enumerate(row):
                col_width[i] = max(col_width[i], len(c))
        rows.insert(1, ['-' * w for w in col_width])
        format = ' | '.join('{:' + ('<' if i == 0 else '>') + str(w) + '}' for i, w in enumerate(col_width))
        for r in rows:
            print(format.format(*r), file=self.stream)


DEFAULT_CSV_COLUMNS = [cols.node_id, cols.name, cols.parent_id, cols.parent_name,
                       cols.total_us, cols.total_inner_us,
                       cols.count, cols.min_us, cols.average_us, cols.max_us]


class CsvReporter:
    def __init__(self, columns=DEFAULT_CSV_COLUMNS, stream=sys.stderr):
        self.columns = columns
        self.stream = stream

    def print_summary(self, rp):
        slices = get_profiler_slice(rp)

        rows = [[col.column_name for col in self.columns]]

        for s in slices:
            row = [col(s, slices) for col in self.columns]
            rows.append(row)

        for r in rows:
            print(', '.join(r), file=self.stream)
