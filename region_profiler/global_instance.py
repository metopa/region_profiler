import atexit
import warnings

from region_profiler.chrome_trace_listener import ChromeTraceListener
from region_profiler.debug_listener import DebugListener
from region_profiler.profiler import RegionProfiler
from region_profiler.reporters import ConsoleReporter
from region_profiler.utils import NullContext

try:
    from region_profiler.cython.profiler import \
        RegionProfiler as CythonRegionProfiler
    has_cython_module = True
except ImportError:
    has_cython_module = False

_profiler = None
"""Global :py:class:`RegionProfiler` instance.

This singleton is initialized using :py:func:`install`.
"""


def install(reporter=ConsoleReporter(), chrome_trace_file=None,
            debug_mode=False, use_cython=True, timer_cls=None):
    """
    Args:
        reporter:
        chrome_trace_file:
        debug_mode:
        use_cython:
        timer_cls:
    """
    global _profiler
    if _profiler is None:
        listeners = []
        if chrome_trace_file:
            listeners.append(ChromeTraceListener(chrome_trace_file))
        if debug_mode:
            listeners.append(DebugListener())

        if use_cython:
            if has_cython_module:
                _profiler = CythonRegionProfiler(listeners=listeners, timer_cls=timer_cls)
            else:
                warnings.warn('Faster profiling with Cython is not available. '
                              'You can enable it by installing Cython and '
                              'then reinstalling region_profiler. '
                              'You can disable this warning by passing use_cython=False.',
                              stacklevel=2)

        if _profiler is None:
            _profiler = RegionProfiler(listeners=listeners, timer_cls=timer_cls)

        _profiler.root.enter_region()
        atexit.register(lambda: reporter.dump_profiler(_profiler))
        atexit.register(lambda: _profiler.finalize())
    else:
        warnings.warn("region_profiler.install() must be called only once", stacklevel=2)
    return _profiler


def region(name=None, asglobal=False):
    """

    Args:
        name:
        asglobal:

    Returns:

    """
    if _profiler is not None:
        return _profiler.region(name, asglobal, 0)
    else:
        return NullContext()


def func(name=None, asglobal=False):
    """

    Args:
        name:
        asglobal:

    Returns:

    """

    def decorator(fn):
        nonlocal name
        if name is None:
            name = fn.__name__

        name += '()'

        def wrapped(*args, **kwargs):
            with region(name, asglobal=asglobal):
                return fn(*args, **kwargs)

        return wrapped

    return decorator


def iter_proxy(iterable, name=None, asglobal=False):
    """

    Args:
        iterable:
        asglobal:
        name:

    Returns:

    """
    if _profiler is not None:
        return _profiler.iter_proxy(iterable, name, asglobal, 0)
    else:
        return iterable
