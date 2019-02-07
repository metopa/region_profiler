import region_profiler as rp
from region_profiler.utils import SeqStats, pretty_print_time


def fact(x):
    return x * fact(x - 1) if x > 1 else x


@rp.func(asglobal=True)
def timed_fact(x):
    return x * timed_fact(x - 1) if x > 1 else x


def main(p):
    reps = 30
    loop_reps = 100
    recursion_depth = 100

    for _ in range(reps):
        for _ in range(loop_reps):
            with rp.region('a'):
                x = fact(recursion_depth)

        for _ in range(loop_reps):
            with rp.region('b1'):
                with rp.region('b2'):
                    x = fact(recursion_depth)

        for _ in range(loop_reps):
            with rp.region('c1'):
                with rp.region('c2'):
                    with rp.region('c3'):
                        x = fact(recursion_depth)

        for _ in range(loop_reps):
            x = timed_fact(recursion_depth)

    nodes = p.root.children
    inner_a = nodes['a'].stats.total / reps  # F + r * loop_reps
    inner_b1 = nodes['b1'].stats.total / reps  # F + r * loop_reps * 2
    inner_b2 = nodes['b1'].children['b2'].stats.total / reps  # F + r * loop_reps
    inner_c1 = nodes['c1'].stats.total / reps  # F + r * loop_reps * 3
    inner_c2 = nodes['c1'].children['c2'].stats.total / reps  # F + r * loop_reps * 2
    inner_c3 = nodes['c1'].children['c2'].children['c3'].stats.total / reps  # F + r * loop_reps
    func = nodes['timed_fact()'].stats.total / reps  # F + r * loop_reps * recursion

    stats = SeqStats()
    stats.add((inner_b1 - inner_b2) / loop_reps)
    stats.add((inner_b1 - inner_a) / loop_reps)
    stats.add((inner_c2 - inner_c3) / loop_reps)
    stats.add((inner_c1 - inner_c2) / loop_reps)
    stats.add((func - inner_a) / (loop_reps * (recursion_depth - 1)))

    print('Region overhead:\n\t{} .. {} .. {}'.
          format(pretty_print_time(stats.min),
                 pretty_print_time(stats.avg),
                 pretty_print_time(stats.max)))


if __name__ == '__main__':
    p = rp.install()
    main(p)
