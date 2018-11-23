import time


class SeqStats:
    def __init__(self):
        self.count = 0
        self.total = 0
        self.max = 0
        self.min = 0

    def add(self, x):
        self.count += 1
        self.total += x
        self.max = x if self.count == 1 else max(self.max, x)
        self.min = x if self.count == 1 else min(self.min, x)

    @property
    def avg(self):
        return 0 if self.count == 0 else self.total / self.count

    def __str__(self):
        return 'SeqStats{{{}..{}..{}/{}}}'.format(self.min, self.avg,
                                                  self.max, self.count)


class Timer:
    """
    Simple timer.

    Allows to measure duration
    between ``start`` and ``stop`` events.

    By default, measurement is done with nanosecond precision.
    This can be changed by providing a different clock as
    ``__init__`` parameter.

    The duration can be retrieved using
    ``current_elapsed()`` and ``total_elapsed()``.
    """
    def __init__(self, clock=lambda: time.perf_counter_ns()):
        """
        :param clock: functor, that returns current clock.
                      Measurements have the same precision as the clock
        """
        self.clock = clock
        self._begin = 0
        self._running = False
        self._total = 0

    def start(self):
        """Start new timer measurement.

        Call this function again to continue measurements.
        """
        self._begin = self.clock()
        self._running = True

    def stop(self):
        """Stop timer and add current measurement to total.

        :return: duration of the last measurement
        :rtype: int, float
        """
        e = self.current_elapsed()
        self._total += e
        self._running = False
        return e

    def current_elapsed(self):
        """Return duration of the current timer leg.

        If timer is running (no ``stop()`` has been called
        after last ``start()`` invocation),
        duration elapsed from last ``start()`` call is returned.

        Otherwise, zero is returned.

        :return: duration after last call to ``start()`` or zero
        :rtype: int, float
        """
        return self.clock() - self._begin if self._running else 0

    def total_elapsed(self):
        """Return total duration across all timer legs.

        If timer is running (no ``stop()`` has been called
        after last ``start()`` invocation),
        duration of the current leg is also added to the total.

        :return: sum of the measured legs
        :rtype: int, float
        """
        return self._total + self.current_elapsed()
