from contextlib import contextmanager

from region_profiler.node import RootNode
from region_profiler.utils import Timer, get_name_by_callsite


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
    """

    ROOT_NODE_NAME = '<main>'

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
        self.root = RootNode(name=self.ROOT_NODE_NAME, timer_cls=timer_cls)
        self.node_stack = [self.root]
        self.listeners = listeners or []
        for l in self.listeners:
            l.region_entered(self, self.root)

    @contextmanager
    def region(self, name=None, asglobal=False, indirect_call_depth=0):
        """Start new region in the current context.

        This function implements context manager interface.
        When used with ``with`` statement,
        it enters a region with the specified name in the current context
        on invocation and leaves it on ``with`` block exit.

        Examples::

            with rp.region('A'):
                ...

        Args:
            name (:py:class:`str`, optional): region name.
                If None, the name is deducted from region location in source
            asglobal (bool): enter the region from root context, not a current one.
                May be used to merge stats from different call paths
            indirect_call_depth (:py:class:`int`, optional): adjust call depth
                to correctly identify the callsite position for automatic naming

        Returns:
            :py:class:`region_profiler.node.RegionNode`: node of the region.
        """
        if name is None:
            name = get_name_by_callsite(indirect_call_depth + 2)
        parent = self.root if asglobal else self.current_node
        self.node_stack.append(parent.get_child(name))
        self._enter_current_region()
        yield self.current_node
        self._exit_current_region()
        self.node_stack.pop()

    def func(self, name=None, asglobal=False):
        """Decorator for entering region on a function call.

        Examples::

            @rp.func()
            def foo():
                ...

        Args:
            name (:py:class:`str`, optional): region name.
                If None, the name is deducted from region location in source
            asglobal (bool): enter the region from root context, not a current one.
                May be used to merge stats from different call paths

        Returns:
            Callable: a decorator for wrapping a function
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

    def iter_proxy(self, iterable, name=None, asglobal=False, indirect_call_depth=0):
        """Wraps an iterable and profiles :func:`next()` calls on this iterable.

        This proxy may be useful, when the iterable is some data loader,
        that performs data retrieval on each iteration.
        For instance, it may pull data from an asynchronous process.

        Such proxy was used to identify that when receiving a batch of
        8 samples from a loader process, first 5 samples were loaded immediately
        (because they were computed asynchronously during the loop body),
        but then it stalled on the last 3 iterations meaning that loading had
        bigger latency than the loop body.

        Examples::

            for batch in rp.iter_proxy(loader):
                ...

        Args:
            iterable (Iterable): an iterable to be wrapped
            name (:py:class:`str`, optional): region name.
                If None, the name is deducted from region location in source
            asglobal (bool): enter the region from root context, not a current one.
                May be used to merge stats from different call paths
            indirect_call_depth (:py:class:`int`, optional): adjust call depth
                to correctly identify the callsite position for automatic naming

        Returns:
            Iterable: an iterable, that yield same data as the passed one
        """
        it = iter(iterable)
        if name is None:
            name = get_name_by_callsite(indirect_call_depth + 1)
        parent = self.root if asglobal else self.current_node
        node = parent.get_child(name)

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
                node of the region as defined above
        """
        return self.node_stack[-1]
