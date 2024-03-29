import arep
import pytest
import ast


ops = arep.utils.ast_mapped_operators()


@pytest.mark.parametrize(('args', 'result'), [
    ([2, 1], False),
    ([1, 2], False),
    ([1, 1], True),
    ([2, 2, 2, 2, 1], False),
    ([2, 2, 2, 2, 2], True),
    (["a", "a", "a"], True),
    (["a", "b", "b"], False),
    ([pytest, pytest], True)
])
def test_eq(args, result):
    assert ops[ast.Eq](*args) == result
