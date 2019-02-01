# cython: language_level=3
# distutils: language=c++

from region_profiler.chrome_trace_listener import ChromeTraceListener as _pyChromeTraceListener
from region_profiler.debug_listener import DebugListener as _pyDebugListener

from region_profiler.cython.listener cimport *

cdef class RegionProfilerListener:
    cdef void finalize(self):
        return

    cdef void region_entered(self, profiler, region):
        return

    cdef void region_exited(self, profiler, region):
        return

    cdef void region_canceled(self, profiler, region):
        return

cdef class PyListenerAdapter(RegionProfilerListener):
    def __init__(self, py_listener):
        self.py_listener = py_listener

    cdef void finalize(self):
        self.py_listener.finalize()

    cdef void region_entered(self, profiler, region):
        self.py_listener.region_entered(profiler, region)

    cdef void region_exited(self, profiler, region):
        self.py_listener.region_exited(profiler, region)

    cdef void region_canceled(self, profiler, region):
        self.py_listener.region_canceled(profiler, region)

cdef class ChromeTraceListener(PyListenerAdapter):
    def __init__(self):
        super().__init__(_pyChromeTraceListener())

cdef class DebugListener(PyListenerAdapter):
    def __init__(self):
        super().__init__(_pyDebugListener())
