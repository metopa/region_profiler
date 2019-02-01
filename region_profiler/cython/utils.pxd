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

    cdef void add(self, double x)


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

    cdef double begin_ts(self)
    cdef double end_ts(self)
    cdef void start(self)
    cdef void stop(self)
    cdef void mark_aux_event(self)
    cdef bool is_running(self)
    cdef double elapsed(self)
    cdef double current_elapsed(self)