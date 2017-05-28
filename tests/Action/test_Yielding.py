from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

results_in_comprehension = results_formatter({
    (3, 5)
})

results_regular = results_formatter({
    (8, 8)
})

results_yield_from = results_formatter({
    (12, 4)
})


all_results = (results_in_comprehension | results_regular | results_yield_from)


@pytest.fixture
def grepper():
    engine = arep.Grepper(os.path.abspath('tests/data/Action/Yielding.py'))
    return engine


@pytest.mark.parametrize(('in_expression'), [True, False, None])
@pytest.mark.parametrize(('from_'), [True, False, None])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Yielding(grepper, action, consideration, from_, in_expression):
    if all([consideration, from_, in_expression]):
        action.reset()
        action.Yielding.in_expression = in_expression
        action.Yielding.from_ = from_
        action.Yielding.consideration = consideration
        grepper.constraint_list.append(action)
        if consideration is not False:
            results = all_results.copy()
        if from_:
            results &= results_yield_from
        elif from_ is False:
            results -= results_yield_from
        if in_expression:
            results &= results_in_comprehension
        elif in_expression is False:
            results -= results_in_comprehension
        assert set(grepper.all_results()) == results
