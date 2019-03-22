# cython: language_level=3
# distutils: language=c++

from region_profiler.utils import default_clock

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

    def __init__(self, int count=0, double total=0, double min=0, double max=0):
        self.count_ = count
        self.total_ = total
        self.min_ = min
        self.max_ = max

    cpdef void add(self, double x):
        """Update statistics with the next value of a sequence.

        Args:
            x (number): next value in the sequence
        """
        self.count_ += 1
        self.total_ += x
        self.max_ = x if self.count_ == 1 else max(self.max_, x)
        self.min_ = x if self.count_ == 1 else min(self.min_, x)

    @property
    def avg(self):
        """Calculate sequence average.
        """
        return 0 if self.count_ == 0 else self.total_ / self.count_

    @property
    def count(self):
        return self.count_

    @property
    def total(self):
        return self.total_

    @property
    def min(self):
        return self.min_

    @property
    def max(self):
        return self.max_

    def __str__(self):
        return 'SeqStats{{{}..{}..{}/{}}}'.format(self.min, self.avg,
                                                  self.max, self.count)

    def __repr__(self):
        return ('SeqStats(count={}, total={}, min={}, max={})'
                .format(self.count, self.total, self.min, self.max))

    def __eq__(self, other):
        return (self.total == other.total and self.count == other.count and
                self.min == other.min and self.max == other.max)


cdef class Timer:
    """Simple timer.

    Allows to measure duration
    between `start` and `stop` events.

    By default, measurement is done with a second scale.
    This can be changed by providing a different clock in constructor.

    The duration can be retrieved using
    :py:meth:`current_elapsed` or :py:meth:`total_elapsed()`.
    """

    def __init__(self, clock=default_clock):
        """
        Args:
            clock(function): functor, that returns current clock.
                      Measurements have the same precision as the clock
        """
        self.clock = clock
        self._begin_ts = 0
        self._end_ts = 0
        self._running = False
        self.last_event_time = 0

    cpdef double begin_ts(self):
        """Start event timestamp.

        Returns:
            int or float: timestamp
        """
        return self._begin_ts

    cpdef double end_ts(self):
        """Stop event timestamp.

        Returns:
            int or float: timestamp
        """
        return self._end_ts

    cpdef void start(self):
        """Start new timer measurement.

        Call this function again to continue measurements.
        """
        self._begin_ts = <double>self.clock()
        self.last_event_time = self._begin_ts
        self._running = True

    cpdef void stop(self):
        """Stop timer and add current measurement to total.

        Returns:
            int or float: duration of the last measurement
        """
        self.last_event_time = <double>self.clock()
        if self._running:
            self._end_ts = self.last_event_time
            self._running = False

    cpdef void mark_aux_event(self):
        """Update ``last_event_time``.
        """
        self.last_event_time = <double>self.clock()

    cpdef bool is_running(self):
        """Check if timer is currently running.

        Returns:
            bool:
        """
        return self._running

    cpdef double elapsed(self):
        """Return duration between `start` and `stop` events.

        If timer is running (no :py:meth:`stop` has been called
        after last :py:meth:`start` invocation), 0 is returned.

        Returns:
            int or float: duration
        """
        return (self._end_ts - self._begin_ts) if not self._running else 0

    cpdef double current_elapsed(self):
        """Return duration between `start` and `stop` events or
        duration from last `start` event if no pairing `stop` event occurred.

        Returns:
            int or float: duration
        """
        return (self._end_ts - self._begin_ts) if not self._running \
            else (self.clock() - self._begin_ts)
