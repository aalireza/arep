from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (2, 4), (6, 8), (15, 12)
})


@pytest.fixture
def grepper():
    engine = arep.Grepper(os.path.abspath('tests/data/Action/Breaking.py'))
    return engine


def test_Breaking(grepper, action):
    action.reset()
    action.Breaking.consideration = True
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == all_results
