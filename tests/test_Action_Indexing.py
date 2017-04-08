from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Indexing', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


all_results = results_formatter({
    (1, 4), (3, 5), (9, 7), (12, 10)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Indexing.py'))
    return engine


def test_Indexing(grepper):
    grepper.add_constraint(hg.Action.Indexing())
    assert set(grepper.get_all_results()) == all_results
