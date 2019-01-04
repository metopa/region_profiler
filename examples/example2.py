import time

import numpy as np
from region_profiler import region, func, iter_proxy, install
install(chrome_trace_file='trace.json')


def slow_iter(iterable):
    for x in iterable:
        time.sleep(0.1)
        yield x


def foo():
    a = np.arange(1000000)
    print('A initialized')
    b = a.copy('')

    for x in slow_iter([1, 2, 3, 4]):
        a += x

    return np.sum(a * b)


@func()  # profile function
def bar():
    with region('init'):  # measure execution time of the next block
        a = np.arange(1000000)

    print('A initialized')

    with region('init'):  # Join region
        b = a.copy('')

    with region('loop'):
        for x in iter_proxy(slow_iter([1, 2, 3, 4]), 'iter'):
            # measure time to retrieve next element
            a += x

    with region():  # autoname region
        return np.sum(a * b)


if __name__ == '__main__':
    print(foo())
    print(bar())