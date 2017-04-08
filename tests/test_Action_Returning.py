from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Returning', 'Line Column')

results_in_lambda = set([])

results_regular = {results_template(x, y) for x, y in {
    (2, 4), (6, 8)
}}

results = (results_regular | results_in_lambda)


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Returning.py'))
    return engine


def test_Returning(grepper):
    grepper.add_constraint(hg.Action.Returning())
    assert results == set(grepper.get_all_results())
