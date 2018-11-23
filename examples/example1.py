from time import sleep

import region_profiler as rp


def foo(n):
    with rp.mark(n):
        with rp.mark('sleep'):
            sleep(0.5)

        with rp.mark('static_loop'):
            for _ in range(1000):
                with rp.mark('outer'):
                    with rp.mark('inner'):
                        pass

        with rp.mark('dynamic_loop'):
            for i in range(1000):
                with rp.mark('outer'):
                    with rp.mark('inner' + str(i % 10)):
                        pass

        with rp.mark('static_loop'):
            for _ in range(1000):
                with rp.mark('outer'):
                    with rp.mark('inner'):
                        pass


if __name__ == '__main__':
    rp.install()
    foo('a')
    foo('a')
    foo('b')
