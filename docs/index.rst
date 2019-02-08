.. Region Profiler documentation master file, created by
   sphinx-quickstart on Tue Dec 25 15:45:00 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Region Profiler - handy Python profiler
#######################################

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



.. image:: https://travis-ci.com/metopa/region_profiler.svg?branch=master
    :target: https://travis-ci.com/metopa/region_profiler
.. image:: https://codecov.io/gh/metopa/region_profiler/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/metopa/region_profiler
.. image:: https://readthedocs.org/projects/region-profiler/badge/?version=latest
    :target: https://region-profiler.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Mark regions using ``with``-statements and decorators.
Time region hierarchy and get detailed console report as well as Chrome Trace log.

Features
========

- **Measure only what you need.** See timing for regions you've marked
  and never waste time on looking at things your not interested in.
- **Measure third party libraries.** You can mark regions inside arbitrary Python package.
  Just don't forget to rollback changes after you've done :)
  Again, only marked regions count. No need to see timings for unfamiliar library internals.
- **No need to use external tools** (like kernprof) to gather profiling data.
  Profile from within your application and use usual command to run it.
- **Average region overhead is 3-10 us** (Python 3.7, Intel Core i5).
- **Chrome Trace log** generation.
- **Table or CSV report format.**
- **Only Cython dependency.**


Why another Python profiler
===========================

While other profilers often focus
on some particular granularity (e.g. function or single line),
Region Profiler allows user to choose the size of the scope of interest
each time, moving from whole function to a subset of lines to a single iteration.

Region Profiler report
contains information only about user-defined regions --
if we are investigating some complicated framework, we don't need to
time its internals outside of the region that we're interested in.

In contrary to majority of existing profilers,
Region Profiler does not require any special programs/switches
(like kernprof) for application start.
This tool is very useful for investigating bottlenecks
of bigger applications, that has complicated start process
(e.g. distributed NN trainer, that is run on a cluster using MPI).

Getting started
===============


Dependencies
------------

- Python >= 3.4
- Cython


Installation
------------

You can install Region Profiler using ``pip``::

    pip install region_profiler

or from sources::

    git clone https://github.com/metopa/region_profiler.git
    cd region_profiler
    python setup.py install

Tutorial
--------

The following snippet shows example usage of Region Profiler::

  import numpy as np
  import region_profiler as rp


  @rp.func()  # profile function
  def f():
      with rp.region('init'):  # measure execution time of the next block
          a = np.arange(1000000)
          b = a.copy('')

      with rp.region('loop'):
          for x in rp.iter_proxy([1, 2, 3, 4], 'iter'):
              # measure time to retrieve next element
              a += x

      with rp.region():  # autoname region
          return np.sum(a * b)


  if __name__ == '__main__':
      rp.install()
      f()

Running this script would yield output similar to this::

  name                  total  % of total  count       min   average       max
  -----------------  --------  ----------  -----  --------  --------  --------
  <main>             31.18 ms     100.00%      1  31.18 ms  31.18 ms  31.18 ms
  . f()              31.09 ms      99.73%      1  31.09 ms  31.09 ms  31.09 ms
  . . init           8.329 ms      26.72%      1  8.329 ms  8.329 ms  8.329 ms
  . . f() <e.py:16>  5.079 ms      16.29%      1  5.079 ms  5.079 ms  5.079 ms
  . . loop           3.134 ms      10.05%      1  3.134 ms  3.134 ms  3.134 ms
  . . . iter         4.573 us       0.01%      4    419 ns  1.143 us  1.779 us


Global regions
--------------

Sometimes we are interested in total running time of a region,
regardless of its caller context. In this case we would like to mark
the region as global.

If we want to measure the forward and backward passes of a neural
network, we can declare ``NN`` class like this (see `<examples/tensorflow_mnist.py>`_ for complete code)::

  class NeuralNet(tfe.Network):
      def __init__(self):
          # Define each layer
          ...

      def call(self, x):
          with rp.region('NN'):
              with rp.region('layer 1'):
                  x = self.layer1(x)
              with rp.region('layer 2'):
                  x = self.layer2(x)
              with rp.region('out layer'):
                  x = self.out_layer(x)
              return x

However, when called from different contexts, ``NN`` region timing would add up to a total.
The profiler summary would look like this. Note that ``NN`` region appears 4 times in the summary::

  name                    total  % of total
  -------------------  --------  ----------
  <main>                12.61 s     100.00%
  . train               11.74 s      93.11%
  . . backward          7.236 s      57.38%
  . . . loss_fn()       2.077 s      16.47%
  . . . . NN            1.790 s      14.19%
  . . . . . layer 1     1.064 s       8.43%
  . . . . . layer 2      526 ms       4.17%
  . . . . . out layer  162.5 ms       1.29%
  . . forward           4.230 s      33.53%
  . . . loss_fn()       2.194 s      17.39%
  . . . . NN            1.880 s      14.91%
  . . . . . layer 1     1.187 s       9.41%
  . . . . . layer 2      506 ms       4.01%
  . . . . . out layer  149.4 ms       1.18%
  . . . accuracy_fn()   1.963 s      15.57%
  . . . . NN            1.703 s      13.50%
  . . . . . layer 1     1.033 s       8.19%
  . . . . . layer 2    491.5 ms       3.90%
  . . . . . out layer  141.6 ms       1.12%
  . . fetch_next       235.3 ms       1.87%
  . test               83.14 ms       0.66%
  . . accuracy_fn()    83.12 ms       0.66%
  . . . NN             81.59 ms       0.65%
  . . . . layer 1      59.41 ms       0.47%
  . . . . layer 2      20.01 ms       0.16%
  . . . . out layer    2.089 ms       0.02%

In order to merge these timings, ``NN`` region should be declared as global::

  class NeuralNet(tfe.Network):
      def __init__(self):
          # Define each layer
          ...

      def call(self, x):
          with rp.region('NN', asglobal=True):
              with rp.region('layer 1'):
                  x = self.layer1(x)
              with rp.region('layer 2'):
                  x = self.layer2(x)
              with rp.region('out layer'):
                  x = self.out_layer(x)
              return x

In this case the summary looks like this::

  name                    total  % of total
  -------------------  --------  ----------
  <main>                12.44 s     100.00%
  . train               11.64 s      93.51%
  . . backward          7.229 s      58.10%
  . . . loss_fn()       2.079 s      16.71%
  . . forward           4.142 s      33.29%
  . . . loss_fn()       2.134 s      17.15%
  . . . accuracy_fn()   1.937 s      15.56%
  . . fetch_next       225.2 ms       1.81%
  . NN                  5.389 s      43.32%
  . . layer 1           3.295 s      26.48%
  . . layer 2           1.544 s      12.41%
  . . out layer        444.0 ms       3.57%
  . test               86.71 ms       0.70%
  . . accuracy_fn()    86.70 ms       0.70%


Chrome Trace
------------

Region Profiler may output log suitable for `Chrome Trace Viewer <https://aras-p.info/blog/2017/01/23/Chrome-Tracing-as-Profiler-Frontend/>`_.

In order to enable such logging, just pass log filename to ``install()`` function::

  rp.install(chrome_trace_file='trace.json')

Then you can open the resulting log in `<chrome://tracing>`_
(obviously, you'd need Chrome browser) for viewing Flame graph of your app execution.
The following Flame graph is for `<examples/tensorflow_mnist.py>`_ sample program.

.. image:: https://github.com/metopa/region_profiler/raw/master/examples/chrome_tracing.png


Documentation
=============

You can find complete API reference `here <https://readthedocs.org/projects/region-profiler/>`_.

The main API consists of these functions:

``region_profiler.install()``
  This function should be called once to enable profiling
  and pass some options to the profiler.

``region_profiler.region()``
  This function returns a context manager that is used to mark a profiling region.
  Allowed parameters:

  - ``name`` - region name.
    If omitted, an automatic name in format ``func() <filename.py:lineno>`` is used.
  - ``as_global`` - mark region as global. See `Global regions`_ section.

``region_profiler.func()``
  Function decorator that wraps the marked function in a region.
  Allowed parameters:

  - ``name`` - region name.
    If omitted, an automatic name in format ``func()`` is used.
  - ``as_global`` - mark region as global. See `Global regions`_ section.

``region_profiler.iter_proxy()``
  Iterable object wrapper. Measures time spent in ``__next__`` on each iteration.
  This wrapper is useful, when iterating over things like ``DataLoader``.
  Allowed parameters:

  - ``name`` - region name.
    If omitted, an automatic name in format ``func() <filename.py:lineno>`` is used.
  - ``as_global`` - mark region as global. See `Global regions`_ section.


License
=======
MIT © Viacheslav Kroilov <slavakroilov@gmail.com>

