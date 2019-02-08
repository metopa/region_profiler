import os
import sys
import threading

from region_profiler.listener import RegionProfilerListener


class ChromeTraceListener(RegionProfilerListener):
    """This listener produces a log, suitable for Chrome Trace Viewer.

    Learn more about `Chrome Trace Viewer
    <https://aras-p.info/blog/2017/01/23/Chrome-Tracing-as-Profiler-Frontend/>`_.
    """

    def __init__(self, trace_filename):
        """Construct ChromeTraceListener.

        Args:
            trace_filename: output .json file
        """
        self.trace_filename = trace_filename
        self.f = open(trace_filename, 'w')
        self.pending_begin_node = None
        self.last_canceled_node = None
        self.f.write('[{{"name": "process_name", "ph": "M", "pid": {}, "tid": {},'
                     '"args": {{"name" : "{}"}}}}'.
                     format(os.getpid(), threading.get_ident(), os.path.basename(sys.argv[0])))
        self.f.write(',\n{{"name": "thread_name", "ph": "M", "pid": {}, "tid": {},'
                     '"args": {{"name" : "Main"}}}}'.
                     format(os.getpid(), threading.get_ident()))

    def finalize(self):
        self.f.write(']')
        self.f.close()
        print('RegionProfiler: Chrome Trace is saved in', self.trace_filename, file=sys.stderr)

    def region_entered(self, profiler, region):
        if self.pending_begin_node:
            self._write_b_event(profiler, self.pending_begin_node)
        self.pending_begin_node = region
        self.last_canceled_node = None

    def region_exited(self, profiler, region):
        if self.pending_begin_node:
            # Skip if current node has been canceled
            if (self.pending_begin_node is region and
                    self.last_canceled_node is self.pending_begin_node):
                self.last_canceled_node = None
                self.pending_begin_node = None
                return
            else:
                self.last_canceled_node = None

            self._write_b_event(profiler, self.pending_begin_node)
            self.pending_begin_node = None
        self._write_e_event(profiler, region)

    def region_canceled(self, profiler, region):
        self.last_canceled_node = region

    def _write_b_event(self, profiler, region):
        self._write_event(region.name, int(region.timer.begin_ts() * 1000000), 'B')

    def _write_e_event(self, profiler, region):
        self._write_event(region.name, int(region.timer.end_ts() * 1000000), 'E')

    def _write_event(self, name, ts, event_type):
        self.f.write(',\n{{"name": "{}", "ph": "{}", "ts": {}, "pid": {}, "tid": {}}}'.
                     format(name, event_type, ts, os.getpid(), threading.get_ident()))
