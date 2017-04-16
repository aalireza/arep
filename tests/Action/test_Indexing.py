from ..utils import action, results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (1, 4), (3, 5), (9, 7), (12, 10)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Indexing.py'))
    return engine


def test_Indexing(grepper, action):
    action.reset()
    action.Indexing.consideration = True
    grepper.add_constraint(action)
    assert set(grepper.get_all_results()) == all_results
