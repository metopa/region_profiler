# cython: language_level=3
# distutils: language=c++

from libcpp cimport bool

cdef class SeqStats:
    """Helper class for calculating online stats of a number sequence.

    :py:class:`SeqStats` records the following parameters of a number sequence:
      - element count
      - sum
      - average
      - min value
      - max value

    :py:class:`SeqStats` does not store the sequence itself,
    statistics are calculated online.
    """
    cdef int count_
    cdef double total_
    cdef double min_
    cdef double max_

    cpdef void add(self, double x)


cdef class Timer:
    """Simple timer.

    Allows to measure duration
    between `start` and `stop` events.

    By default, measurement is done with a second scale.
    This can be changed by providing a different clock in constructor.

    The duration can be retrieved using
    :py:meth:`current_elapsed` or :py:meth:`total_elapsed()`.
    """

    cdef object clock
    cdef double _begin_ts
    cdef double _end_ts
    cdef double last_event_time
    cdef bool _running

    cpdef double begin_ts(self)
    cpdef double end_ts(self)
    cpdef void start(self)
    cpdef void stop(self)
    cpdef void mark_aux_event(self)
    cpdef bool is_running(self)
    cpdef double elapsed(self)
    cpdef double current_elapsed(self)