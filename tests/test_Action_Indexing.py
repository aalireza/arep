from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Indexing', 'Line Column')

results = {results_template(x, y) for x, y in {
    (1, 4), (3, 5), (9, 7), (12, 10)
}}


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Indexing.py'))
    return engine


def test_Indexing(grepper):
    grepper.add_constraint(hg.Action.Indexing())
    assert results == set(grepper.get_all_results())
