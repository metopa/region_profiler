import sys
from collections import OrderedDict

from region_profiler.utils import SeqStats, Timer


class RegionNode:
    def __init__(self, name, timer_cls=Timer):
        self.name = name
        self.timer = None
        self.stats = SeqStats()
        self.timer_cls = timer_cls
        self.children = OrderedDict()

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
        return self.name or '<root>'
