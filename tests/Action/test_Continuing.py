from ..utils import results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (5, 8), (9, 8)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Continuing.py'))
    return engine


def test_Continuing(grepper):
    grepper.add_constraint(hg.Action.Continuing())
    assert set(grepper.get_all_results()) == all_results
