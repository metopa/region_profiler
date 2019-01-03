import atexit
import warnings
from contextlib import contextmanager

from region_profiler.node import RootNode
from region_profiler.reporters import ConsoleReporter
from region_profiler.utils import (NullContext, Timer, get_name_by_callsite,
                                   null_decorator)


class RegionProfiler:
    """:py:class:`RegionProfiler` handles code regions profiling.

    This is the central class in :py:mod:`region_profiler` package.
    It is responsible for maintaining the hierarchy of timed regions
    as well as providing facilities for marking regions for timing
    using

      - ``with``-statement (:py:meth:`RegionProfiler.region`)
      - function decorator (:py:meth:`RegionProfiler.func`)
      - an iterator proxy (:py:meth:`RegionProfiler.iter_proxy`)

    Normally it is expected that the global instance of
    :py:class:`RegionProfiler` is used for the profiling,
    see package-level function :py:func:`region_profiler.install`,
    :py:func:`region_profiler.region`, :py:func:`region_profiler.func`,
    and :py:func:`region_profiler.iter_proxy`.

    Todo:
        Code examples
    """

    def __init__(self, timer_cls=Timer):
        """Construct new :py:class:`RegionProfiler`.

        Args:
            timer_cls (:obj:`class`, optional): class, used for creating timers.
                Default: ``region_profiler.utils.Timer``
        """
        self.root = RootNode(timer_cls=timer_cls)
        self.node_stack = [self.root]

    @contextmanager
    def region(self, name=None, indirect_call_depth=0):
        """Start new region in the current context.

        Args:
            name:
            indirect_call_depth:

        Returns:

        """
        if name is None:
            name = get_name_by_callsite(indirect_call_depth + 2)
        self.node_stack.append(self.current_node.get_child(name))
        self.current_node.enter_region()
        yield self.current_node
        self.current_node.exit_region()
        self.node_stack.pop()

    def func(self, name=None):
        """

        Args:
            name:

        Returns:

        """

        def decorator(fn):
            nonlocal name
            if name is None:
                name = fn.__name__

            name += '()'

            def wrapped(*args, **kwargs):
                with self.region(name):
                    return fn(*args, **kwargs)

            return wrapped

        return decorator

    def iter_proxy(self, iterable, name=None, indirect_call_depth=0):
        """

        Args:
            iterable:
            name:
            indirect_call_depth:

        Returns:

        """
        it = iter(iterable)
        if name is None:
            name = get_name_by_callsite(indirect_call_depth + 2)

        node = self.current_node.get_child(name)

        while True:
            self.node_stack.append(node)
            node.enter_region()
            try:
                x = next(it)
            except StopIteration as e:
                node.cancel_region()
                return
            finally:
                node.exit_region()
                self.node_stack.pop()
                
            yield x

    @property
    def current_node(self):
        """

        Returns:

        """
        return self.node_stack[-1]


_profiler = None


def install(reporter=ConsoleReporter(), timer_cls=Timer):
    """

    Args:
        reporter:

    Returns:

    """
    global _profiler
    if _profiler is None:
        _profiler = RegionProfiler(timer_cls=timer_cls)
        _profiler.root.enter_region()
        atexit.register(lambda: reporter.dump_profiler(_profiler))
        atexit.register(lambda: _profiler.root.exit_region())
    else:
        warnings.warn("region_profiler.install() must be called only once", stacklevel=2)


def region(name=None):
    """

    Args:
        name:

    Returns:

    """
    if _profiler is not None:
        return _profiler.region(name, 0)
    else:
        return NullContext()


def func(name=None):
    """

    Args:
        name:

    Returns:

    """
    if _profiler is not None:
        return _profiler.func(name)
    else:
        return null_decorator()


def iter_proxy(iterable, name=None):
    """

    Args:
        iterable:
        name:

    Returns:

    """
    if _profiler is not None:
        return _profiler.iter_proxy(iterable, name, -1)
    else:
        return iterable
