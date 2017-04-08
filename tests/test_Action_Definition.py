from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Definition', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


all_results = results_formatter({
    (1, 0), (6, 0), (14, 0), (18, 0), (26, 0), (7, 4), (15, 4), (20, 4),
    (27, 4), (21, 8)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Definition.py'))
    return engine


def test_Definition(grepper):
    grepper.add_constraint(hg.Action.Definition())
    assert set(grepper.get_all_results()) == all_results
