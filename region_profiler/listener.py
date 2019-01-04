from abc import abstractmethod


class RegionProfilerListener:
    @abstractmethod
    def finalize(self):
        pass

    @abstractmethod
    def region_entered(self, profiler, region):
        pass

    @abstractmethod
    def region_exited(self, profiler, region):
        pass

    @abstractmethod
    def region_canceled(self, profiler, region):
        pass
