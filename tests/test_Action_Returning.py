from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Returning', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


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


def test_Returning(grepper):
    grepper.add_constraint(hg.Action.Returning())
    assert set(grepper.get_all_results()) == all_results
