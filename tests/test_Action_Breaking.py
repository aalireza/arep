from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Breaking', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


all_results = results_formatter({
    (2, 4), (6, 8), (15, 12)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Breaking.py'))
    return engine


def test_Breaking(grepper):
    grepper.add_constraint(hg.Action.Breaking())
    assert set(grepper.get_all_results()) == all_results
