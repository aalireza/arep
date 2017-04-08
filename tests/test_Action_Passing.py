from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Passing', 'Line Column')

results = {results_template(x, y) for x, y in {
    (2, 4), (10, 8)
}}


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Passing.py'))
    return engine


def test_Passing(grepper):
    grepper.add_constraint(hg.Action.Passing())
    assert results == set(grepper.get_all_results())
