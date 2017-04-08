from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Breaking', 'Line Column')

results = {results_template(x, y) for x, y in {
    (2, 4), (6, 8), (15, 12)
}}


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Breaking.py'))
    return engine


def test_Breaking(grepper):
    grepper.add_constraint(hg.Action.Breaking())
    assert results == set(grepper.get_all_results())
