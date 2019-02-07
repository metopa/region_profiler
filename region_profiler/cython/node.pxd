# cython: language_level=3
# distutils: language=c++

from region_profiler.cython.utils cimport SeqStats, Timer
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

    cdef readonly str name
    cdef readonly bool optimized_class
    cdef readonly object timer_cls
    cdef readonly Timer timer
    cdef readonly bool cancelled
    cdef readonly SeqStats stats
    cdef readonly dict children
    cdef readonly int recursion_depth

    cpdef void enter_region(self)

    cpdef void cancel_region(self)

    cpdef void exit_region(self)

    cpdef RegionNode get_child(self, str name, timer_cls= *)

    cdef bool timer_is_active(self)


cdef class _RootNodeStats(SeqStats):
    """Proxy object that wraps timer in the
    :py:class:`region_profiler.utils.SeqStats` interface.

    Timer is expected to have the same interface as
    :py:class:`region_profiler.utils.Timer` object.
    Proxy properties return current timer values.
    """
    cdef Timer timer

cdef class RootNode(RegionNode):
    """An instance of :any:`RootNode` is intended to be used
    as the root of a region node hierarchy.

    :any:`RootNode` differs from :any:`RegionNode`
    by making :py:attr:`RegionNode.stats` property
    returning the current measurement values instead of
    the real stats of previous measurements.
    """

    cpdef void cancel_region(self)

    cpdef void exit_region(self)
