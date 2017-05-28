from ..utils import action, results_formatter
from functools import partial
import arep
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (1, 0), (6, 0), (14, 0), (18, 0), (26, 0), (7, 4), (15, 4), (20, 4),
    (27, 4), (21, 8)
})


@pytest.fixture
def grepper():
    engine = arep.Grepper(os.path.abspath('tests/data/Action/Definition.py'))
    return engine


def test_Definition(grepper, action):
    action.reset()
    action.Definition.consideration = True
    grepper.constraint_list.append(action)
    assert set(grepper.all_results()) == all_results
