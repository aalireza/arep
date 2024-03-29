from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (3, 0), (6, 4)
})


@pytest.fixture
def grepper():
    engine = arep.Grepper(
        os.path.abspath('tests/data/Action/Making_Global.py')
    )
    return engine


def test_Making_Global(grepper, action):
    action.reset()
    action.Making_Global.consideration = True
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == all_results


@pytest.mark.parametrize(('name', 'result'), [
    ('x', all_results),
    ('y', set([]))
])
@pytest.mark.parametrize(('consideration'), [True, None])
def test_Making_Global_name(grepper, action, consideration, name, result):
    action.reset()
    action.Making_Global.name = name
    action.Making_Global.consideration = consideration
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == results_formatter(result)
