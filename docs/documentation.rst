
API
===

You can find complete API reference `here <https://region-profiler.readthedocs.io/en/latest/region_profiler.html>`_.

The main API consists of these functions:

:func:`region_profiler.install`
  This function should be called once to enable profiling
  and pass some options to the profiler.

:func:`region_profiler.region`
  This function returns a context manager that is used to mark a profiling region.
  Allowed parameters:

  - ``name`` - region name.
    If omitted, an automatic name in format ``func() <filename.py:lineno>`` is used.
  - ``as_global`` - mark region as global. See :ref:`Global regions` section.

:func:`region_profiler.func`
  Function decorator that wraps the marked function in a region.
  Allowed parameters:

  - ``name`` - region name.
    If omitted, an automatic name in format ``func()`` is used.
  - ``as_global`` - mark region as global. See :ref:`Global regions` section.

:func:`region_profiler.iter_proxy`
  Iterable object wrapper. Measures time spent in ``__next__`` on each iteration.
  This wrapper is useful, when iterating over things like ``DataLoader``.
  Allowed parameters:

  - ``name`` - region name.
    If omitted, an automatic name in format ``func() <filename.py:lineno>`` is used.
  - ``as_global`` - mark region as global. See :ref:`Global regions`. section.
