# cython: language_level=3
# distutils: language=c++

cdef class RegionProfilerListener:
    cdef void finalize(self)
    cdef void region_entered(self, profiler, region)
    cdef void region_exited(self, profiler, region)
    cdef void region_canceled(self, profiler, region)

cdef class PyListenerAdapter(RegionProfilerListener):
    cdef object py_listener

    cdef void finalize(self)
    cdef void region_entered(self, profiler, region)
    cdef void region_exited(self, profiler, region)
    cdef void region_canceled(self, profiler, region)

cdef class ChromeTraceListener(PyListenerAdapter):
    pass

cdef class DebugListener(PyListenerAdapter):
    pass
