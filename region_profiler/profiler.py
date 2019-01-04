import atexit
import warnings
from contextlib import contextmanager

from region_profiler.chrome_trace_listener import ChromeTraceListener
from region_profiler.debug_listener import DebugListener
from region_profiler.node import RootNode
from region_profiler.reporters import ConsoleReporter
from region_profiler.utils import (NullContext, Timer, get_name_by_callsite)


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

    ROOT_NODE_NAME = '<main>'

    def __init__(self, timer_cls=Timer, listeners=None):
        """Construct new :py:class:`RegionProfiler`.

        Args:
            timer_cls (:obj:`class`, optional): class, used for creating timers.
                Default: ``region_profiler.utils.Timer``
            listeners (:py:class:`list` of
                :py:class:`region_profiler.listener.RegionProfilerListener`, optional):
                optional list of listeners, that can augment region enter and exit events.
        """
        self.root = RootNode(name=self.ROOT_NODE_NAME, timer_cls=timer_cls)
        self.node_stack = [self.root]
        self.listeners = listeners or []
        for l in self.listeners:
            l.region_entered(self, self.root)

    @contextmanager
    def region(self, name=None, indirect_call_depth=0):
        """Start new region in the current context.

        This function implements context manager interface.
        When used with ``with`` statement,
        it enters a region with the specified name in the current context
        on invocation and leaves it on ``with`` block exit.

        Args:
            name (:py:class:`str`, optional): region name.
                If None, the name is deducted from region location in source
            indirect_call_depth (:py:class:`int`, optional):

        Returns:
            :py:class:`region_profiler.node.RegionNode`: node of the region.
        """
        if name is None:
            name = get_name_by_callsite(indirect_call_depth + 2)
        self.node_stack.append(self.current_node.get_child(name))
        self._enter_current_region()
        yield self.current_node
        self._exit_current_region()
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
            self._enter_current_region()
            try:
                x = next(it)
            except StopIteration as e:
                self._cancel_current_region()
                return
            finally:
                self._exit_current_region()
                self.node_stack.pop()

            yield x

    def finalize(self):
        """Perform profiler finalization on application shutdown.
        Finalize all associated listeners.
        """
        self.root.exit_region()
        for l in self.listeners:
            l.region_exited(self, self.root)
            l.finalize()

    def _enter_current_region(self):
        self.current_node.enter_region()
        for l in self.listeners:
            l.region_entered(self, self.current_node)

    def _exit_current_region(self):
        self.current_node.exit_region()
        for l in self.listeners:
            l.region_exited(self, self.current_node)

    def _cancel_current_region(self):
        self.current_node.cancel_region()
        for l in self.listeners:
            l.region_canceled(self, self.current_node)

    @property
    def current_node(self):
        """Return current region node.

        Returns:
            :py:class:`region_profiler.node.RegionNode`:
                node of the region as defined above.
        """
        return self.node_stack[-1]


_profiler = None
"""Global :py:class:`RegionProfiler` instance.

This singleton is initialized using :py:func:`install`.
"""


def install(reporter=ConsoleReporter(), chrome_trace_file=None,
            debug_mode=False, timer_cls=Timer):
    """

    Args:
        reporter:
        timer_cls:
        chrome_trace_file:
    """
    global _profiler
    if _profiler is None:
        listeners = []
        if chrome_trace_file:
            listeners.append(ChromeTraceListener(chrome_trace_file))
        if debug_mode:
            listeners.append(DebugListener())
        _profiler = RegionProfiler(listeners=listeners, timer_cls=timer_cls)
        _profiler.root.enter_region()
        atexit.register(lambda: reporter.dump_profiler(_profiler))
        atexit.register(lambda: _profiler.finalize())
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

    def decorator(fn):
        nonlocal name
        if name is None:
            name = fn.__name__

        name += '()'

        def wrapped(*args, **kwargs):
            with region(name):
                return fn(*args, **kwargs)

        return wrapped

    return decorator


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
