import sys
import time
import region_profiler as rp
from region_profiler.reporters import ConsoleReporter


def func_name():
    return f'{sys._getframe(1).f_code.co_name}()'


def demo_hand_decorated():
    time.sleep(1)


def slow_iter(iterable):
    for ii in iterable:
        time.sleep(1)
        yield ii

##############################################################################
# Local profiler instance
##############################################################################


def demo_local_context_mgr(mrp):
    # context manager with local rp instance
    with mrp.region(func_name()):
        time.sleep(1)


def demo_local_region_hand_code(mrp):
    # hand code region with local rp instance - no indent
    rn = mrp.current_node.get_child(func_name())
    rn.enter_region()

    time.sleep(1)

    rn.exit_region()


def l_demo_heir(mrp):

    for ii in range(2):
        # call via "decorated" local rp instance
        mrp.func()(demo_hand_decorated)()

    demo_local_context_mgr(mrp)
    demo_local_region_hand_code(mrp)

    for ii in mrp.iter_proxy(slow_iter(range(2)), slow_iter.__name__):
        pass


def demo_local():

    # make a "local" profiler
    mrp = rp.RegionProfiler()
    mrp.root.enter_region()

    # call via "decorated" local rp instance - passing arg
    mrp.func()(l_demo_heir)(mrp)

    # report the local profiler - before program ends
    ConsoleReporter().dump_profiler(mrp)
    mrp.finalize()


##############################################################################
# Global profiler module
##############################################################################


@rp.func()
def demo_global_function_decorator():
    time.sleep(1)


def demo_global_context_mgr():
    with rp.region(func_name()):
        time.sleep(1)


@rp.func()
def g_demo_heir():

    for ii in range(2):
        # call via "decorated" global rp instance
        rp.func()(demo_hand_decorated)()

    demo_global_context_mgr()
    demo_global_function_decorator()

    for ii in rp.iter_proxy(slow_iter(range(2)), slow_iter.__name__):
        pass


def demo_global():
    # make a profiler in global modul profiler
    rp.install()

    g_demo_heir()

    # print global module on program exit...


def main(argv=None):
    if not argv:
        argv = sys.argv

    print('***local profiler - print before exit')
    demo_local()

    print('\n***global profiler - similar result')
    demo_global()


if __name__ == '__main__':
    sys.exit(main())
