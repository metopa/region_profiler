import os
import sys
import threading

from region_profiler.listener import RegionProfilerListener


class ChromeTraceListener(RegionProfilerListener):
    def __init__(self, trace_filename):
        self.trace_filename = trace_filename
        self.f = open(trace_filename, 'w')
        self.need_comma = False
        self.f.write('[')

    def finalize(self):
        self.f.write(']')
        self.f.close()
        print('RegionProfiler: Chrome Trace is saved at', self.trace_filename, file=sys.stderr)

    def region_entered(self, profiler, region):
        assert region.timer is not None, "Timer is not enabled"
        self.write_event(region.name, int(region.timer.begin_ts() * 1000000), 'B')

    def region_exited(self, profiler, region):
        assert region.timer is not None, "Timer is not enabled"
        self.write_event(region.name, int(region.timer.end_ts() * 1000000), 'E')

    def region_canceled(self, profiler, region):
        pass

    def write_event(self, name, ts, event_type):
        if self.need_comma:
            self.f.write(',')
        else:
            self.need_comma = True
        self.f.write('{{"name": "{}", "ph": "{}", "ts": {}, "pid": {}, "tid": {}}}'.
                     format(name, event_type, ts, os.getpid(), threading.get_ident()))
