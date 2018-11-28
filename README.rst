``region_profiler`` - profile custom regions of code
====================================================
.. image:: https://travis-ci.com/metopa/region_profiler.svg?branch=master
    :target: https://travis-ci.com/metopa/region_profiler
.. image:: https://codecov.io/gh/metopa/region_profiler/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/metopa/region_profiler

:Synopsis: Profile user-defined regions of code without
           any external tools. Explicitly defined regions
           are specified by its name, so you can profile
           the same snippet as different regions under
           different conditions. Regions can
           span from a whole function call to a single
           statement to single iteration inside a loop.
:Author: Viacheslav Kroilov <slavakroilov@gmail.com>

:TODO: - Append region mode
       - Region labels
           - Track func arguments
           - Track separate iterations
       - Support Chrome Trace
       - Export as CSV
       - Better dump
       - Fix decorator called before ``install()``

