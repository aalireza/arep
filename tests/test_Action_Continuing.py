from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Continuing', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


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
