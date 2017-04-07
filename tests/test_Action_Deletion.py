from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Deletion', 'Line Column')

results = {results_template(x, y) for x, y in {(2, 0), (13, 12)}}


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Deletion.py'))
    return engine


def test_Deletion(grepper):
    grepper.add_constraint(hg.Action.Deletion())
    assert results == set(grepper.get_all_results())
