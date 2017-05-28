from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (4, 4), (5, 0), (6, 0), (15, 4), (6, 6), (9, 11), (9, 15)
})


@pytest.fixture
def grepper():
    engine = arep.Grepper(os.path.abspath('tests/data/Action/Call.py'))
    return engine


def test_Call(grepper, action):
    action.reset()
    action.Call.consideration = True
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == all_results
