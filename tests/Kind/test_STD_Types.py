from ..utils import kind, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (1, 6), (7, 8), (9, 7), (9, 18)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Kind/STD_Types.py'))
    return engine


def test_STD_Types(grepper, kind):
    kind.reset()
    kind.STD_Types.consideration = True
    grepper.add_constraint(kind)
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('type_', 'result'), [
    (str, {(7, 8), (9, 18)}),
    (int, {(1, 6)}),
    (dict, set([])),
])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_STD_Types_type(grepper, kind, type_, consideration, result):
    kind.reset()
    kind.STD_Types.type_ = type_
    kind.STD_Types.consideration = consideration
    grepper.add_constraint(kind)
    assert set(grepper.get_all_results()) == results_formatter(result)
