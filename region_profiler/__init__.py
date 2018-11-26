"""
:mod:`region_profiler` -- profile custom regions of code
========================================================

.. module:: region_profiler
   :synopsis: Profile user-defined regions of code without
              any external tools. Explicitly defined regions
              are specified by its name, so you can profile
              the same snippet as different regions under
              different conditions. Regions can
              span from a whole function call to a single
              statement to single iteration inside a loop.
.. moduleauthor:: Viacheslav Kroilov <slavakroilov@gmail.com>
"""

from .profiler import *

__all__ = ['install', 'region', 'func', 'RegionProfiler']
