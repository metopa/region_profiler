import atexit
import warnings
from typing import Any, Callable, Iterable, List, Optional, TypeVar

from region_profiler.chrome_trace_listener import ChromeTraceListener
from region_profiler.debug_listener import DebugListener
from region_profiler.listener import RegionProfilerListener
from region_profiler.profiler import RegionProfiler
from region_profiler.reporters import ConsoleReporter
from region_profiler.utils import NullContext, Timer

_profiler = None
"""Global :py:class:`RegionProfiler` instance.

This singleton is initialized using :py:func:`install`.
"""

F = TypeVar("F", bound=Callable[..., Any])


def install(
    reporter=ConsoleReporter(),
    chrome_trace_file: Optional[str] = None,
    debug_mode: bool = False,
    timer_cls: Optional[Callable[[], Timer]] = None,
    torch_synchronize: bool = True,
) -> RegionProfiler:
    """Enable profiling.

    Initialize a global profiler with user arguments
    and register its finalization at application exit.

    Args:
        reporter (:py:class:`region_profiler.reporters.ConsoleReporter`):
            The reporter used to print out the final summary.
            Provided profilers:

            - :py:class:`region_profiler.reporters.ConsoleReporter`
            - :py:class:`region_profiler.reporters.CsvReporter`

        chrome_trace_file (:py:class:`str`, optional): path to the output trace file.
            If provided, Chrome Trace generation is enable and the resulting trace is saved under this name.
        debug_mode (:py:class:`bool`, default=False):
            Enable verbose logging for profiler events.
            See :py:class:`region_profiler.debug_listener.DebugListener`
        timer_cls: (:py:obj:`region_profiler.utils.Timer`):
            Pass custom timer constructor. Mainly useful for testing.
    """
    global _profiler
    if _profiler is None:
        listeners: List[RegionProfilerListener] = []
        if chrome_trace_file:
            listeners.append(ChromeTraceListener(chrome_trace_file))
        if debug_mode:
            listeners.append(DebugListener())

        _profiler = RegionProfiler(
            listeners=listeners,
            timer_cls=timer_cls,
            torch_synchronize=torch_synchronize,
        )

        _profiler.root.enter_region()
        atexit.register(lambda: reporter.dump_profiler(_profiler))
        atexit.register(lambda: _profiler.finalize())  # type: ignore[union-attr]
    else:
        warnings.warn(
            "region_profiler.install() must be called only once", stacklevel=2
        )
    return _profiler


def uninstall():
    global _profiler
    _profiler = None


def region(name: Optional[str] = None, asglobal: bool = False):
    """Start new region in the current context.

    This function implements context manager interface.
    When used with ``with`` statement,
    it enters a region with the specified name in the current context
    on invocation and leaves it on ``with`` block exit.

    Examples::

        with rp.region('A'):
            ...

    Args:
        name (:py:class:`str`, optional): region name.
            If None, the name is deducted from region location in source
        asglobal (bool): enter the region from root context, not a current one.
            May be used to merge stats from different call paths

    Returns:
        :py:class:`region_profiler.node.RegionNode`: node of the region.
    """
    if _profiler is not None:
        return _profiler.region(name, asglobal, 0)
    else:
        return NullContext()


def func(name: Optional[str] = None, asglobal: bool = False) -> Callable[[F], F]:
    """Decorator (factory) for entering region on a function call.

    Examples::

        @rp.func()
        def foo():
            ...

    Args:
        name (:py:class:`str`, optional): region name.
            If None, the name is deducted from region location in source
        asglobal (bool): enter the region from root context, not a current one.
            May be used to merge stats from different call paths

    Returns:
        Callable: a decorator for wrapping a function
    """

    # We can't just use _profiler?.func() here because this function, as well as
    # decorator() will execute on import, before rp.install() can be called. So
    # we can't be conditional on _profiler until we're inside wrapped(), and
    # region() already does that.
    def decorator(fn):
        nonlocal name
        if name is None:
            name = fn.__name__

        name += "()"

        def wrapped(*args, **kwargs):
            with region(name, asglobal=asglobal):
                return fn(*args, **kwargs)

        return wrapped

    return decorator


def iter_proxy(
    iterable: Iterable, name: Optional[str] = None, asglobal: bool = False
) -> Iterable:
    """Wraps an iterable and profiles :func:`next()` calls on this iterable.

    This proxy may be useful, when the iterable is some data loader,
    that performs data retrieval on each iteration.
    For instance, it may pull data from an asynchronous process.

    Such proxy was used to identify that when receiving a batch of
    8 samples from a loader process, first 5 samples were loaded immediately
    (because they were computed asynchronously during the loop body),
    but then it stalled on the last 3 iterations meaning that loading had
    bigger latency than the loop body.

    Examples::

        for batch in rp.iter_proxy(loader):
            ...

    Args:
        iterable (Iterable): an iterable to be wrapped
        name (:py:class:`str`, optional): region name.
            If None, the name is deducted from region location in source
        asglobal (bool): enter the region from root context, not a current one.
            May be used to merge stats from different call paths

    Returns:
        Iterable: an iterable, that yield same data as the passed one
    """
    if _profiler is not None:
        return _profiler.iter_proxy(iterable, name, asglobal, 0)
    else:
        return iterable
