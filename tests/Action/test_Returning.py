from ..utils import action, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

results_in_lambda = results_formatter(set([]))

results_regular = results_formatter({
    (2, 4), (6, 8)
})

all_results = (results_regular | results_in_lambda)


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Returning.py'))
    return engine


def test_Returning(grepper, action):
    action.reset()
    action.Returning.consideration = True
    grepper.add_constraint(action)
    assert set(grepper.get_all_results()) == all_results
