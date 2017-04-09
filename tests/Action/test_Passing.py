from ..utils import results_formatter
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


def test_Passing(grepper):
    grepper.add_constraint(hg.Action.Passing())
    assert all_results == set(grepper.get_all_results())
