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
    Simple timer object.

    States:
      -------
      |Steady               --start()-> Running --stop-> Stopped
       -------------------
       elapsed() returns 0              elapsed() returns duration passed after last start

    """
    def __init__(self, clock=time.perf_counter_ns):
        self.clock = clock
        self._begin = 0
        self._end = 0
        self._running = False

    def start(self):
        self._begin = self.clock()
        self._running = True

    def stop(self):
        """
        Stop
        :return:
        """
        if self._running:
            self._end = self.clock()
            self._running = False

    def elapsed(self):
        """Return timed duration in nanoseconds.

        If timer is running (no ``stop()`` has been called
        after last ``start()`` invocation),
        duration elapsed from last start() call is returned.

        Otherwise, duration between last consecutive calls to
        ``start()`` and ``stop()`` is returned.

        :return: int
        """
        if self._running:
            return self.clock() - self._begin
        else:
            return self._end - self._begin
