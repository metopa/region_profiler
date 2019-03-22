# cython: language_level=3
# distutils: language=c++

import warnings

from region_profiler.cython.utils cimport SeqStats, Timer
from region_profiler.cython.node cimport RegionNode, RootNode, _RootNodeStats

from libcpp cimport bool

cdef class RegionNode:
    """RegionNode represents a single entry in a region tree.

    It contains a builtin timer for measuring the time, spent
    in the corresponding region. It keeps a track of
    the count, sum, max and min measurements.
    These statistics can be accessed through :py:attr:`stats` attribute.

    In addition, RegionNode has a dictionary of its children.
    They are expected to be retrieved using :py:meth:`get_child`,
    that also creates a new child if necessary.

    Attributes:
        name (str): Node name.
        stats (SeqStats): Measurement statistics.
    """

    def __init__(self, str name, timer_cls=Timer):
        """Create new instance of ``RegionNode`` with the given name.

        Args:
            name (str): node name
            timer_cls (class): class, used for creating timers.
                Default: ``region_profiler.utils.Timer``
        """
        self.name = name
        self.optimized_class = True
        self.timer_cls = timer_cls
        self.timer = self.timer_cls()
        self.cancelled = False
        self.stats = SeqStats()
        self.children = dict()
        self.recursion_depth = 0

    cpdef void enter_region(self):
        """Start timing current region.
        """
        if self.recursion_depth == 0:
            self.timer.start()
        else:
            self.timer.mark_aux_event()

        self.cancelled = False
        self.recursion_depth += 1

    cpdef void cancel_region(self):
        """Cancel current region timing.

        Stats will not be updated with the current measurement.
        """
        self.cancelled = True
        self.recursion_depth -= 1
        if self.recursion_depth == 0:
            self.timer.stop()
        else:
            self.timer.mark_aux_event()

    cpdef void exit_region(self):
        """Stop current timing and update stats with the current measurement.
        """
        if self.cancelled:
            self.cancelled = False
            self.timer.mark_aux_event()
        else:
            self.recursion_depth -= 1
            if self.recursion_depth == 0:
                self.timer.stop()
                self.stats.add(self.timer.elapsed())
            else:
                self.timer.mark_aux_event()

    cpdef RegionNode get_child(self, str name, timer_cls=None):
        """Get node child with the given name.

        This method creates a new child and stores it
        in the inner dictionary if it has not been created yet.
        
        TODO:
            Optimize Cython code
        
        Args:
            name (str): child name
            timer_cls (:obj:`class`, optional): override child timer class

        Returns:
            RegionNode: new or existing child node with the given name
        """
        cdef RegionNode c
        try:
            return <RegionNode> self.children[name]
        except KeyError:
            c = RegionNode(name, timer_cls if timer_cls is not None else self.timer_cls)
            self.children[name] = c
            return c

    cdef bool timer_is_active(self):
        """Return True if timer is currently running.
        """
        return self.recursion_depth > 1 or self.recursion_depth == 1 and self.cancelled

    def __str__(self):
        return self.name or '???'

    def __repr__(self):
        return 'RegionNode(name="{}", stats={}, timer_cls={})'. \
            format(str(self), repr(self.stats), self.timer_cls)


cdef class _RootNodeStats:
    """Proxy object that wraps timer in the
    :py:class:`region_profiler.utils.SeqStats` interface.

    Timer is expected to have the same interface as
    :py:class:`region_profiler.utils.Timer` object.
    Proxy properties return current timer values.
    """
    def __init__(self, timer):
        self.timer = timer

    @property
    def count(self):
        return 1

    @property
    def total(self):
        return self.timer.current_elapsed()

    @property
    def min(self):
        return self.total

    @property
    def max(self):
        return self.total


cdef class RootNode(RegionNode):
    """An instance of :any:`RootNode` is intended to be used
    as the root of a region node hierarchy.

    :any:`RootNode` differs from :any:`RegionNode`
    by making :py:attr:`RegionNode.stats` property
    returning the current measurement values instead of
    the real stats of previous measurements.
    """

    def __init__(self, str name='<root>', timer_cls=Timer):
        super().__init__(name, timer_cls)
        self.enter_region()
        self.stats = _RootNodeStats(self.timer)

    cpdef void cancel_region(self):
        """Prevents root region from being cancelled.
        """
        warnings.warn('Can\'t cancel root region timer', stacklevel=2)

    cpdef void exit_region(self):
        """Instead of :py:meth:`RegionNode.exit_region` it does not reset
        :py:attr:`timer` attribute thus allowing it to continue timing on reenter.
        """
        self.timer.stop()
