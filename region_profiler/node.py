from region_profiler.utils import SeqStats


class RegionNode:
    def __init__(self, name):
        self.name = name
        self.stats = SeqStats()
