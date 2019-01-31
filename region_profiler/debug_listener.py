import sys

from region_profiler.listener import RegionProfilerListener
from region_profiler.utils import pretty_print_time


class DebugListener(RegionProfilerListener):
    def finalize(self):
        print('RegionProfiler: Finalizing profiler', file=sys.stderr)

    def region_entered(self, profiler, region):
        ts = region.timer.last_event_time - profiler.root.timer.begin_ts()
        print('RegionProfiler: Entered {} at {}'.
              format(region.name, pretty_print_time(ts)), file=sys.stderr)

    def region_exited(self, profiler, region):
        ts = region.timer.last_event_time - profiler.root.timer.begin_ts()
        elapsed = region.timer.last_event_time - region.timer.begin_ts()
        print('RegionProfiler: Exited {} at {} after {}'.
              format(region.name, pretty_print_time(ts),
                     pretty_print_time(elapsed)),
              file=sys.stderr)

    def region_canceled(self, profiler, region):
        ts = region.timer.last_event_time - profiler.root.timer.begin_ts()
        print('RegionProfiler: Canceled {} at {}'.format(region.name, pretty_print_time(ts)), file=sys.stderr)
