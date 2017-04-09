import higher_grep as hg
import pytest


ops = hg.core._ast_mapped_operators()


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
    assert ops['Eq'](*args) == result
