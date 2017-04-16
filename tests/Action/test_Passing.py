from ..utils import action, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (2, 4), (10, 8)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Passing.py'))
    return engine


def test_Passing(grepper, action):
    action.reset()
    action.Passing.consideration = True
    grepper.add_constraint(action)
    assert set(grepper.get_all_results()) == all_results
