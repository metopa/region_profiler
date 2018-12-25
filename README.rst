``region_profiler`` - profile custom regions of code
====================================================
.. image:: https://travis-ci.com/metopa/region_profiler.svg?branch=master
    :target: https://travis-ci.com/metopa/region_profiler
.. image:: https://codecov.io/gh/metopa/region_profiler/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/metopa/region_profiler
.. image:: https://readthedocs.org/projects/region-profiler/badge/?version=latest
    :target: https://region-profiler.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

:Synopsis: Effortlessly profile user-defined regions of code.
:Author: Viacheslav Kroilov <slavakroilov@gmail.com>
:Description: Region Profiler allows you to time execution of Python code snippets.
     Measured snippets are called regions. A region
     is specified by its name, so you can profile
     the same snippet as different regions under
     different conditions. Regions can
     span from a whole function call to a single
     statement to single iteration inside a loop.
     You can mark any part of code
     as a region, including internal routines of some third-party package.

     In contrary to majority of existing profilers,
     Region Profiler does not require any special programs/switches
     (like kernprof) for application start. In addition, the final report
     contains information only about user-defined regions --
     if we are investigation some complicated framework, we don't need to
     see/learn its internals outside of the scope of interest.

     This tool is extremely useful when investigating bottlenecks
     of bigger applications, that has complicated start process
     (e.g. distributed NN trainer, that is run on a cluster using MPI).

     Basic usage example is there:
     https://github.com/metopa/region_profiler/blob/master/examples/example2.py

     Additional features:

     - Real-time Chrome trace export
     - Speed up profiling with Cython module
     - CSV/human-readable summary export

:TODO: - Append region mode
       - Region labels
           - Track func arguments
           - Track separate iterations
       - Support Chrome Trace
       - Export as CSV
       - Better dump
       - Fix decorator called before ``install()``

