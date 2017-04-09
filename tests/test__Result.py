import higher_grep as hg
import pytest


def results_formatter(*results):
    return [hg.core.Result(n, x, y) for n, x, y in results][0]


@pytest.mark.parametrize(('left', 'right'), [
    [("a", 1, 1), ("a", 1, 1)],
    [("test.py._asd", 256, 256), ("test.py._asd", 256, 256)]
])
def test_eq(left, right):
    assert results_formatter(left) == results_formatter(right)


@pytest.mark.parametrize(('left', 'right'), [
    [("a", 1, 1), ("a", 2, 1)],
    [("b", 256, 256), ("c", 256, 256)]
])
def test_neq(left, right):
    assert results_formatter(left) != results_formatter(right)


@pytest.mark.parametrize(('left', 'right'), [
    [("a", 1, 1), ("a", 2, 1)],
    [("a", 1, 1), ("a", 1, 2)],
    [("a", 1, 5), ("a", 2, 2)],
])
def test_lt(left, right):
    assert results_formatter(left) < results_formatter(right)
