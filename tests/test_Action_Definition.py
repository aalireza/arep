from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Call', 'Line Column')

results = {
    results_template(x, y)
    for x, y in {(1, 0), (6, 0), (14, 0), (18, 0), (26, 0), (7, 4), (15, 4),
                 (20, 4), (27, 4), (21, 8)}
}


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Definition.py'))
    return engine


def test_Definition(grepper):
    grepper.add_constraint(hg.Action.Definition())
    assert results == set(grepper.get_all_results())
