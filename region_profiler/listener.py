from abc import abstractmethod


class RegionProfilerListener:
    @abstractmethod
    def finalize(self):
        raise NotImplementedError

    @abstractmethod
    def region_entered(self, profiler, region):
        raise NotImplementedError

    @abstractmethod
    def region_exited(self, profiler, region):
        raise NotImplementedError

    @abstractmethod
    def region_canceled(self, profiler, region):
        raise NotImplementedError
