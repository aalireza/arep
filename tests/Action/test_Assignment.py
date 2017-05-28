from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

aug_assign_results = results_formatter({
    (9, 4)
})

all_results = results_formatter({
    (5, 0), (11, 0), (12, 0), (16, 0), (18, 0), (2, 4), (8, 4), (9, 4)
})


@pytest.fixture
def grepper():
    engine = arep.Grepper(os.path.abspath('tests/data/Action/Assignment.py'))
    return engine


@pytest.mark.parametrize(('AugAssign'), [True, False, None])
@pytest.mark.parametrize(('Assign'), [True, False, None])
def test_Assignment(grepper, action, Assign, AugAssign):
    action.reset()
    results = set()
    if any([Assign, AugAssign]):
        action.Assignment.consideration = Assign
        action.Assignment.Operational_Augmentation.consideration = AugAssign
        if Assign is not False:
            results = all_results.copy()
        if AugAssign:
            results &= aug_assign_results
        elif AugAssign is False:
            results -= aug_assign_results
        grepper.constraint_list.append(action)
        assert set(grepper.all_results()) == results


@pytest.mark.parametrize(('symbol', 'results'), [
    ('+', {(9, 4)}),
    ('-', set([]))
])
def test_Assignment_augmented_symbol(grepper, action, symbol, results):
    action.reset()
    action.Assignment.Operational_Augmentation.operation_symbol = symbol
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == results_formatter(results)
