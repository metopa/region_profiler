from abc import abstractmethod


class RegionProfilerListener:
    """Base class for profiler listeners, that can augment profiler functionality.

    Profiler listeners can execute custom hooks on the following events:

    - Enter region
    - Exit region
    - Cancel region
    - Finish profiling
    """

    @abstractmethod
    def finalize(self):
        """Hook 'Finish profiling' event.
        """
        raise NotImplementedError

    @abstractmethod
    def region_entered(self, profiler, region):
        """Hook 'Enter region' event.

        Args:
            profiler (:py:class:`region_profiler.profiler.RegionProfiler`):
                Profiler instance
            region (:py:class:`region_profiler.node.RegionNode`):
                Region associated with the event
        """
        raise NotImplementedError

    @abstractmethod
    def region_exited(self, profiler, region):
        """Hook 'Exit region' event.

        Args:
            profiler (:py:class:`region_profiler.profiler.RegionProfiler`):
                Profiler instance
            region (:py:class:`region_profiler.node.RegionNode`):
                Region associated with the event
        """
        raise NotImplementedError

    @abstractmethod
    def region_canceled(self, profiler, region):
        """Hook 'Cancel region' event.

        Args:
            profiler (:py:class:`region_profiler.profiler.RegionProfiler`):
                Profiler instance
            region (:py:class:`region_profiler.node.RegionNode`):
                Region associated with the event
        """
        raise NotImplementedError
