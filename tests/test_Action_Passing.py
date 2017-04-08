from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Passing', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


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
