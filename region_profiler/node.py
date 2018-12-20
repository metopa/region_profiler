import sys
import warnings

from region_profiler.utils import SeqStats, Timer


class RegionNode:
    def __init__(self, name, timer_cls=Timer):
        self.name = name
        self.timer = None
        self.stats = SeqStats()
        self.timer_cls = timer_cls
        self.children = dict()

    def enter_region(self):
        if self.timer is None:
            self.timer = self.timer_cls()

        self.timer.start()

    def cancel_region(self):
        self.timer = None

    def exit_region(self):
        if self.timer is not None:
            self.timer.stop()
            self.stats.add(self.timer.total_elapsed())
            self.timer = None

    def get_child(self, name, timer_cls=None):
        try:
            return self.children[name]
        except KeyError:
            c = RegionNode(name, timer_cls or self.timer_cls)
            self.children[name] = c
            return c

    def dump(self, depth=0):
        print('{}{} [{:.3f} ms/{}]'.format('  ' * depth, str(self),
                                           self.stats.avg * 1000,
                                           self.stats.count),
              file=sys.stderr)
        for c in self.children.values():
            c.dump(depth + 1)

    def __str__(self):
        return self.name or '???'


class _RootNodeStats:
    def __init__(self, timer):
        self.timer = timer

    @property
    def count(self):
        return 1

    @property
    def total(self):
        return self.timer.total_elapsed()

    @property
    def min(self):
        return self.total

    @property
    def max(self):
        return self.total


class RootNode(RegionNode):
    def __init__(self, timer_cls=Timer):
        super(RootNode, self).__init__('<root>', timer_cls)
        self.timer = timer_cls()
        self.stats = _RootNodeStats(self.timer)

    def cancel_region(self):
        warnings.warn('Can\'t cancel root region timer', stacklevel=2)

    def exit_region(self):
        self.timer.stop()
