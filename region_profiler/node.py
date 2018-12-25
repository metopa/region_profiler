import sys
import warnings

from region_profiler.utils import SeqStats, Timer


class RegionNode:
    """RegionNode represents a single entry in a region tree.

    It contains a builtin timer for measuring the time, spent
    in the corresponding region. It keeps a track of
    the count, sum, max and min measurements.
    These statistics can be accessed through ``stats`` attribute.

    In addition, RegionNode has a dictionary of its children.
    They are expected to be retrieved with ``get_child`` method,
    that creates a new child if necessary.

    Attributes:
        name (str): node name
        stats (SeqStats): measurement statistics
    """
    def __init__(self, name, timer_cls=Timer):
        """Create new instance of ``RegionNode`` with the given name.

        Args:
            name (str): node name
            timer_cls (class): class, used for creating timers.
                Default: ``region_profiler.utils.Timer``
        """
        self.name = name
        self.timer = None
        self.stats = SeqStats()
        self.timer_cls = timer_cls
        self.children = dict()

    def enter_region(self):
        """Start timing current region.
        """
        if self.timer is None:
            self.timer = self.timer_cls()

        self.timer.start()

    def cancel_region(self):
        """Cancel current region timing.

        Do not update measurement stats.
        """
        self.timer = None

    def exit_region(self):
        """Stop current timing and update stats with the current measurement.
        """
        if self.timer is not None:
            self.timer.stop()
            self.stats.add(self.timer.total_elapsed())
            self.timer = None

    def get_child(self, name, timer_cls=None):
        """Get node child with the given name.

        This method creates a new child and stores it
        in the inner dictionary if it has not been created yet.

        Args:
            name (str): child name
            timer_cls (class, optional): override child timer class

        Returns:
            RegionNode: new or existing child node with the given name
        """
        try:
            return self.children[name]
        except KeyError:
            c = RegionNode(name, timer_cls or self.timer_cls)
            self.children[name] = c
            return c

    def __str__(self):
        return self.name or '???'

    def __repr__(self):
        return 'RegionNode(name="{}", stats={}, timer_cls={})'.\
            format(str(self), repr(self.stats), self.timer_cls)


class _RootNodeStats:
    """Proxy object that wraps timer in the
    ``region_profiler.utils.SeqStats`` interface.

    Timer is expected to have the same interface as
    ``region_profiler.utils.Timer`` object.
    Proxy properties return current timer values.
    """
    def __init__(self, timer):
        self.timer = timer

    @property
    def count(self):
        return 1

    @property
    def total(self):
        return self.timer.total_elapsed()

    @property
    def min(self):
        return self.total

    @property
    def max(self):
        return self.total


class RootNode(RegionNode):
    """An instance of ``RootNode`` is intended to be used
    as the root of a region node hierarchy.

    ``RootNode`` differs from ``RegionNode``
    by making ``stats`` property returning the current
    measurement values instead of a real stats
    of previous measurements.
    """
    def __init__(self, timer_cls=Timer):
        super(RootNode, self).__init__('<root>', timer_cls)
        self.timer = timer_cls()
        self.stats = _RootNodeStats(self.timer)

    def cancel_region(self):
        """Prevents root region from being cancelled.
        """
        warnings.warn('Can\'t cancel root region timer', stacklevel=2)

    def exit_region(self):
        """Instead of :meth:`RegionNode.exit_region` it does not reset
        ``timer`` attribute thus allowing it to continue timing on reenter.
        """
        self.timer.stop()
