# cython: language_level=3
# distutils: language=c++

from region_profiler.cython.node cimport RegionNode, RootNode


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

    cdef readonly RootNode root
    cdef list node_stack
    cdef list listeners

    cpdef void finalize(self)

    cdef void _enter_current_region(self)

    cdef void _exit_current_region(self)

    cdef void _cancel_current_region(self)

    cdef RegionNode current_node_c(self)
