from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (2, 4), (10, 8)
})


@pytest.fixture
def grepper():
    engine = arep.Grepper(os.path.abspath('tests/data/Action/Passing.py'))
    return engine


def test_Passing(grepper, action):
    action.reset()
    action.Passing.consideration = True
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == all_results
