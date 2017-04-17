from ..utils import action, results_formatter
from functools import partial
import higher_grep as hg
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
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Assignment.py'))
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
        grepper.add_constraint(action)
        assert set(grepper.get_all_results()) == results