from region_profiler.listener import RegionProfilerListener


class DebugListener(RegionProfilerListener):
    def finalize(self):
        print('Finalizing profiler')

    def region_entered(self, profiler, region):
        print('Entered {} at {}'.format(region.name, region.timer.begin_ts()))

    def region_exited(self, profiler, region):
        print('Exited {} at {} after {}'.
              format(region.name, region.timer.begin_ts(), region.timer.elapsed()))

    def region_canceled(self, profiler, region):
        pass