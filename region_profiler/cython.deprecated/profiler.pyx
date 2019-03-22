# cython: language_level=3
# distutils: language=c++

from contextlib import contextmanager

from region_profiler.utils import get_name_by_callsite
from region_profiler.profiler import RegionProfiler as PyRegionProfiler

from region_profiler.cython.node cimport RegionNode, RootNode
from region_profiler.cython.utils cimport Timer
from region_profiler.cython.listener cimport RegionProfilerListener, PyListenerAdapter
from libcpp cimport bool

cdef str ROOT_NODE_NAME = <str> PyRegionProfiler.ROOT_NODE_NAME

cdef class RegionProfiler:
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

    def __init__(self, timer_cls=None, listeners=None):
        """Construct new :py:class:`RegionProfiler`.

        Args:
            timer_cls (:obj:`class`, optional): class, used for creating timers.
                Default: ``region_profiler.utils.Timer``
            listeners (:py:class:`list` of
                :py:class:`region_profiler.listener.RegionProfilerListener`, optional):
                optional list of listeners, that can augment region enter and exit events.
        """
        if timer_cls is None:
            timer_cls = Timer
        self.root = RootNode(name=ROOT_NODE_NAME, timer_cls=timer_cls)
        self.node_stack = [self.root]
        if listeners is None:
            listeners = []

        self.listeners = [l if isinstance(l, RegionProfilerListener)
                          else PyListenerAdapter(l) for l in listeners]

        cdef RegionProfilerListener ll
        for pl in self.listeners:
            ll = <RegionProfilerListener>pl
            ll.region_entered(self, self.root)

    @contextmanager
    def region(self, str name=None, bool asglobal=False, int indirect_call_depth=0):
        """Start new region in the current context.

        This function implements context manager interface.
        When used with ``with`` statement,
        it enters a region with the specified name in the current context
        on invocation and leaves it on ``with`` block exit.

        Args:
            name (:py:class:`str`, optional): region name.
                If None, the name is deducted from region location in source
            asglobal (bool): enter the region from root context, no current one.
                May be used to merge stats from different call paths
            indirect_call_depth (:py:class:`int`, optional): adjust call depth
                to correctly identify the callsite position for automatic naming

        Returns:
            :py:class:`region_profiler.node.RegionNode`: node of the region.
        """
        if name is None:
            name = get_name_by_callsite(indirect_call_depth + 1)
        cdef RegionNode parent = self.root if asglobal is True else self.current_node_c()
        self.node_stack.append(parent.get_child(name))
        self._enter_current_region()
        yield self.current_node_c()
        self._exit_current_region()
        self.node_stack.pop()

    def func(self, str name=None, bool asglobal=False):
        """

        Args:
            name (:py:class:`str`, optional): region name.
                If None, the name is deducted from region location in source
            asglobal (bool): enter the region from root context, no current one.
                May be used to merge stats from different call paths

        Returns:

        """

        def decorator(fn):
            nonlocal name
            if name is None:
                name = fn.__name__

            name += '()'

            def wrapped(*args, **kwargs):
                with self.region(name, asglobal):
                    return fn(*args, **kwargs)

            return wrapped

        return decorator

    def iter_proxy(self, object iterable, str name=None,
                   bool asglobal=False, int indirect_call_depth=0):
        """

        Args:
            iterable:
            name:
            asglobal:
            indirect_call_depth:

        Returns:

        """
        cdef object it = iter(iterable)
        if name is None:
            name = get_name_by_callsite(indirect_call_depth)
        cdef RegionNode parent = self.root if asglobal is True else self.current_node_c()
        cdef RegionNode node = parent.get_child(name)

        while True:
            self.node_stack.append(node)
            self._enter_current_region()
            try:
                x = next(it)
            except StopIteration:
                self._cancel_current_region()
                return
            finally:
                self._exit_current_region()
                self.node_stack.pop()

            yield x

    cpdef void finalize(self):
        """Perform profiler finalization on application shutdown.
        Finalize all associated listeners.
        """
        self.root.exit_region()
        cdef RegionProfilerListener l
        for pl in self.listeners:
            l = <RegionProfilerListener>pl
            l.region_exited(self, self.root)
            l.finalize()

    cdef void _enter_current_region(self):
        self.current_node_c().enter_region()
        cdef RegionProfilerListener l
        for pl in self.listeners:
            l = <RegionProfilerListener>pl
            l.region_entered(self, self.current_node_c())

    cdef void _exit_current_region(self):
        self.current_node_c().exit_region()
        cdef RegionProfilerListener l
        for pl in self.listeners:
            l = <RegionProfilerListener>pl
            l.region_exited(self, self.current_node_c())


    cdef void _cancel_current_region(self):
        self.current_node_c().cancel_region()
        cdef RegionProfilerListener l
        for pl in self.listeners:
            l = <RegionProfilerListener>pl
            l.region_canceled(self, self.current_node_c())


    @property
    def current_node(self):
        """Return current region node.

        Returns:
            :py:class:`region_profiler.node.RegionNode`:
                node of the region as defined above.
        """
        return self.node_stack[-1]

    cdef RegionNode current_node_c(self):
        """Return current region node.

        Returns:
            :py:class:`region_profiler.node.RegionNode`:
                node of the region as defined above.
        """
        return <RegionNode> self.node_stack[-1]
