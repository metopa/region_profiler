import pytest

from region_profiler.utils import (NullContext, null_decorator,
                                   pretty_print_time)


def test_pretty_print_time():
    assert pretty_print_time(666) == '666 s'
    assert pretty_print_time(100.44) == '100.4 s'
    assert pretty_print_time(10.044) == '10.04 s'
    assert pretty_print_time(1.0044) == '1.004 s'
    assert pretty_print_time(0.13244) == '132.4 ms'
    assert pretty_print_time(0.013244) == '13.24 ms'
    assert pretty_print_time(0.0013244) == '1.324 ms'
    assert pretty_print_time(0.00013244) == '132.4 us'
    assert pretty_print_time(0.000013244) == '13.24 us'
    assert pretty_print_time(0.0000013244) == '1.324 us'
    assert pretty_print_time(0.00000013244) == '132.44 ns'


def test_null_context():
    """Test null context.
    """
    with NullContext() as c:
        assert True

    with pytest.raises(RuntimeError):
        with NullContext() as c:
            raise RuntimeError('Dummy')


def test_null_decorator():
    """Test null decorator.
    """
    @null_decorator()
    def foo():
        return 42

    assert foo() == 42
