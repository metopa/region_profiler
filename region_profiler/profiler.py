import warnings
from contextlib import contextmanager

import atexit

from region_profiler.node import RegionNode
from region_profiler.utils import Timer, get_name_by_callsite, NullContext, null_decorator


class RegionProfiler:
    def __init__(self, timer_cls=Timer):
        self.root = RegionNode('<main>', timer_cls=timer_cls)
        self.node_stack = [self.root]

    @contextmanager
    def region(self, name=None, indirect_call_depth=0):
        if name is None:
            name = get_name_by_callsite(indirect_call_depth + 2)
        self.node_stack.append(self.current_node.get_child(name))
        self.current_node.enter_region()
        yield self.current_node
        self.current_node.exit_region()
        self.node_stack.pop()

    def func(self, name=None):
        def decorator(fn):
            nonlocal name
            if name is None:
                name = fn.__name__

            def wrapped(*args, **kwargs):
                with self.region(name):
                    return fn(*args, **kwargs)

            return wrapped

        return decorator

    def iter_proxy(self, iterable, name=None, indirect_call_depth=0):
        it = iter(iterable)
        if name is None:
            name = get_name_by_callsite(indirect_call_depth + 2)

        self.node_stack.append(self.current_node.get_child(name))
        try:
            while True:
                self.current_node.enter_region()
                try:
                    x = next(it)
                except StopIteration as e:
                    self.current_node.cancel_region()
                    return
                self.current_node.exit_region()
                yield x
        finally:
            self.current_node.exit_region()
            self.node_stack.pop()

    def dump(self):
        print('', end='', flush=True)
        self.root.dump()

    @property
    def current_node(self):
        return self.node_stack[-1]


_profiler = None


def install():
    global _profiler
    if _profiler is None:
        _profiler = RegionProfiler()
        _profiler.root.enter_region()
        atexit.register(lambda: _profiler.dump())
        atexit.register(lambda: _profiler.root.exit_region())
    else:
        warnings.warn("region_profiler.install() must be called only once", stacklevel=2)


def region(name=None):
    if _profiler is not None:
        return _profiler.region(name, 0)
    else:
        return NullContext()


def func(name=None):
    if _profiler is not None:
        return _profiler.func(name)
    else:
        return null_decorator()


def iter_proxy(iterable, name=None):
    if _profiler is not None:
        return _profiler.iter_proxy(iterable, name, -1)
    else:
        return iterable
