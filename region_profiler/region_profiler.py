from contextlib import contextmanager

import atexit

from region_profiler.node import RegionNode
from region_profiler.utils import Timer


class RegionProfiler:
    def __init__(self, timer_cls=Timer):
        self.root = RegionNode('<main>', timer_cls=timer_cls)
        self.node_stack = [self.root]

    @contextmanager
    def mark(self, name):
        self.node_stack.append(self.current_node.get_child(name))
        self.current_node.enter_region()
        yield
        self.current_node.exit_region()
        self.node_stack.pop()

    def dump(self):
        self.root.dump()

    @property
    def current_node(self):
        return self.node_stack[-1]


_profiler = RegionProfiler()


def mark(name):
    return _profiler.mark(name)


def install():
    atexit.register(lambda: _profiler.dump())
