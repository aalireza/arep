from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (3, 8), (11, 8), (14, 12)
})


@pytest.fixture
def grepper():
    engine = arep.Grepper(
        os.path.abspath('tests/data/Action/Making_Nonlocal.py')
    )
    return engine


def test_Making_Nonlocal(grepper, action):
    action.reset()
    action.Making_Nonlocal.consideration = True
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == all_results


@pytest.mark.parametrize(('name', 'result'), [
    ('x', (all_results - results_formatter({(14, 12)}))),
    ('y', {(14, 12)}),
    ('z', set([]))
])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Making_Nonlocal_name(grepper, action, consideration, name,
                              result):
    action.reset()
    action.Making_Nonlocal.name = name
    action.Making_Nonlocal.consideration = consideration
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == results_formatter(result)
