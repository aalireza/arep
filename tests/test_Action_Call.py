from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Call', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


all_results = results_formatter({
    (4, 4), (5, 0), (6, 0), (15, 4), (6, 6), (9, 11), (9, 15)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Call.py'))
    return engine


def test_call(grepper):
    grepper.add_constraint(hg.Action.Call())
    assert set(grepper.get_all_results()) == all_results
