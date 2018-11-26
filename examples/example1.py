from time import sleep

import region_profiler as rp


def foo(n):
    with rp.region(n):
        with rp.region('sleep'):
            sleep(0.5)

        with rp.region('static_loop'):
            for _ in range(1000):
                with rp.region('outer'):
                    with rp.region('inner'):
                        pass

        with rp.region('dynamic_loop'):
            for i in range(1000):
                with rp.region('outer'):
                    with rp.region('inner' + str(i % 10)):
                        pass

        with rp.region('static_loop'):
            for _ in range(1000):
                with rp.region('outer'):
                    with rp.region('inner'):
                        pass


if __name__ == '__main__':
    rp.install()
    foo('a')
    foo('a')
    foo('b')
