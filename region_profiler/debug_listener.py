import sys

from region_profiler.listener import RegionProfilerListener
from region_profiler.utils import pretty_print_time


class DebugListener(RegionProfilerListener):
    """Log profiler events to console.

    This listener log enter/exit events in real time. Sample output::

        RegionProfiler: Entered <main> at 0 ns
        RegionProfiler: Entered fetch_mnist() at 641 us
        RegionProfiler: Exited fetch_mnist() at 643 ms after 642 ms
        RegionProfiler: Entered train at 743 ms
        RegionProfiler: Entered fetch_next at 743 ms
        RegionProfiler: Exited fetch_next at 744 ms after 1.183 ms
        RegionProfiler: Entered forward at 744 ms
        RegionProfiler: Entered loss_fn() at 744 ms
        RegionProfiler: Entered NN at 745 ms
        RegionProfiler: Exited NN at 764 ms after 19.40 ms
        RegionProfiler: Exited loss_fn() at 765 ms after 20.55 ms
        RegionProfiler: Exited <main> at 1.066 s after 1.066 s
        RegionProfiler: Finalizing profiler
    """
    def finalize(self):
        """Log 'Finish profiling' event.
        """
        print('RegionProfiler: Finalizing profiler', file=sys.stderr)

    def region_entered(self, profiler, region):
        """Log 'Enter region' event.
        """
        ts = region.timer.last_event_time - profiler.root.timer.begin_ts()
        print('RegionProfiler: Entered {} at {}'.
              format(region.name, pretty_print_time(ts)), file=sys.stderr)

    def region_exited(self, profiler, region):
        """Log 'Exit region' event.
        """
        ts = region.timer.last_event_time - profiler.root.timer.begin_ts()
        elapsed = region.timer.last_event_time - region.timer.begin_ts()
        print('RegionProfiler: Exited {} at {} after {}'.
              format(region.name, pretty_print_time(ts),
                     pretty_print_time(elapsed)),
              file=sys.stderr)

    def region_canceled(self, profiler, region):
        """Log 'Exit region' event.
        """
        ts = region.timer.last_event_time - profiler.root.timer.begin_ts()
        print('RegionProfiler: Canceled {} at {}'.format(region.name, pretty_print_time(ts)), file=sys.stderr)
