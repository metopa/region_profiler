from region_profiler.utils import get_caller_info


def func_a(tester):
    """Helper function for ``test_get_caller_info()``
    """
    tester()


def func_b(tester):
    """Helper function for ``test_get_caller_info()``
    """
    func_a(tester)


def test_get_caller_info():
    """Assert that ``get_caller_info()`` return meaningful values.
    """
    def tester():
        a_info = get_caller_info(1)
        print(a_info)
        assert a_info.name == 'func_a'
        assert a_info.file == __file__
        assert a_info.line == 7

        b_info = get_caller_info(2)
        print(b_info)

        assert b_info.name == 'func_b'
        assert b_info.file == __file__
        assert b_info.line == 13

    func_b(tester)
