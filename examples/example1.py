from time import sleep

import region_profiler as rp


def foo(n):
    with rp.checkpoint(n):
        with rp.checkpoint('sleep'):
            sleep(0.5)

        with rp.checkpoint('static_loop'):
            for _ in range(1000):
                with rp.checkpoint('outer'):
                    with rp.checkpoint('inner'):
                        pass

        with rp.checkpoint('dynamic_loop'):
            for i in range(1000):
                with rp.checkpoint('outer'):
                    with rp.checkpoint('inner' + str(i % 10)):
                        pass

        with rp.checkpoint('static_loop'):
            for _ in range(1000):
                with rp.checkpoint('outer'):
                    with rp.checkpoint('inner'):
                        pass


if __name__ == '__main__':
    rp.install()
    foo('a')
    foo('a')
    foo('b')
