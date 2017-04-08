from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Deletion', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


all_results = results_formatter({
    (2, 0), (13, 12)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Deletion.py'))
    return engine


def test_Deletion(grepper):
    grepper.add_constraint(hg.Action.Deletion())
    assert set(grepper.get_all_results()) == all_results
