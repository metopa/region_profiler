import inspect
import os
import time
from collections import namedtuple


class SeqStats:
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

    def __init__(self, count=0, total=0, min=0, max=0):
        self.count = count
        self.total = total
        self.min = min
        self.max = max

    def add(self, x):
        """Update statistics with the next value of a sequence.

        Args:
            x (number): next value in the sequence
        """
        self.count += 1
        self.total += x
        self.max = x if self.count == 1 else max(self.max, x)
        self.min = x if self.count == 1 else min(self.min, x)

    @property
    def avg(self):
        """Calculate sequence average.
        """
        return 0 if self.count == 0 else self.total / self.count

    def __str__(self):
        return 'SeqStats{{{}..{}..{}/{}}}'.format(self.min, self.avg,
                                                  self.max, self.count)

    def __repr__(self):
        return ('SeqStats(count={}, total={}, min={}, max={})'
                .format(self.count, self.total, self.min, self.max))

    def __eq__(self, other):
        return (self.total == other.total and self.count == other.count and
                self.min == other.min and self.max == other.max)


def default_clock():
    """Default clock provider for Timer class.

    Returns:
        float: value (in fractional seconds) of a performance counter
    """
    return time.perf_counter()


class Timer:
    """Simple timer.

    Allows to measure duration between `start` and `stop` events.

    By default, measurement is done on a fractions of a second scale.
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

    def begin_ts(self):
        """Start event timestamp.

        Returns:
            int or float: timestamp
        """
        return self._begin_ts

    def end_ts(self):
        """Stop event timestamp.

        Returns:
            int or float: timestamp
        """
        return self._end_ts

    def start(self):
        """Start new timer measurement.

        Call this function again to continue measurements.
        """
        self._begin_ts = self.clock()
        self.last_event_time = self._begin_ts
        self._running = True

    def stop(self):
        """Stop timer and add current measurement to total.

        Returns:
            int or float: duration of the last measurement
        """
        self.last_event_time = self.clock()
        if self._running:
            self._end_ts = self.last_event_time
            self._running = False

    def mark_aux_event(self):
        """Update ``last_event_time``.
        """
        self.last_event_time = self.clock()

    def is_running(self):
        """Check if timer is currently running.

        Returns:
            bool:
        """
        return self._running

    def elapsed(self):
        """Return duration between `start` and `stop` events.

        If timer is running (no :py:meth:`stop` has been called
        after last :py:meth:`start` invocation), 0 is returned.

        Returns:
            int or float: duration
        """
        return (self._end_ts - self._begin_ts) if not self._running else 0

    def current_elapsed(self):
        """Return duration between `start` and `stop` events or
        duration from last `start` event if no pairing `stop` event occurred.

        Returns:
            int or float: duration
        """
        return (self._end_ts - self._begin_ts) if not self._running \
            else (self.clock() - self._begin_ts)


CallerInfo = namedtuple('CallerInfo', ['file', 'line', 'name'])


def get_caller_info(stack_depth=1):
    """
    Return caller function name and
    call site filename and line number.

    Args:
        stack_depth (int): select caller frame to be inspected.

                        - 0 corresponds to the call site of
                          the :py:func:`get_caller_info` itself.
                        - 1 corresponds to the call site of
                          the parent function.

    Returns:
        CallerInfo:  information about the caller

    """
    frame = inspect.stack()[stack_depth + 1]
    info = CallerInfo(frame[1], frame[2], frame[3])
    del frame  # prevents cycle reference
    return info


def get_name_by_callsite(stack_depth=1):
    """Get string description of the call site
    of the caller.

    Args:
        stack_depth: select caller frame to be inspected.

                        - 0 corresponds to the call site of
                          the :py:meth:`get_name_by_callsite` itself.
                        - 1 corresponds to the call site of
                          the parent function.

    Returns:
        str: string in the following format: ``'function<filename:line>'``
    """
    info = get_caller_info(stack_depth + 1)
    f = os.path.basename(info.file)
    return '{}() <{}:{}>'.format(info.name, f, info.line)


class NullContext:
    """Empty context manager.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def null_decorator():
    """Empty decorator.
    """
    return lambda fn: fn


def pretty_print_time(sec):
    """Get duration as a human-readable string.

    Examples:

        - 10.044 => '10.04 s'
        - 0.13244 => '132.4 ms'
        - 0.0000013244 => '1.324 us'

    Args:
        sec (float): duration in fractional seconds scale

    Returns:
        str: human-readable string representation as shown above.
    """
    for unit in ('s', 'ms', 'us'):
        if sec >= 500:
            return '{:.0f} {}'.format(sec, unit)
        if sec >= 100:
            return '{:.1f} {}'.format(sec, unit)
        if sec >= 10:
            return '{:.2f} {}'.format(sec, unit)
        if sec >= 1:
            return '{:.3f} {}'.format(sec, unit)
        sec *= 1000

    return '{} ns'.format(int(sec))
