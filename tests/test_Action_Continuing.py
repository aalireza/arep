from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Continuing', 'Line Column')

results = {results_template(x, y) for x, y in {
    (5, 8), (9, 8)
}}


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Continuing.py'))
    return engine


def test_Continuing(grepper):
    grepper.add_constraint(hg.Action.Continuing())
    assert results == set(grepper.get_all_results())
