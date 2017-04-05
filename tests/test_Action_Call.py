from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Call', 'Line Column')

results = {results_template(x, y)
           for x, y in {(4, 4), (5, 0), (6, 0), (15, 4),
                        (6, 6), (9, 11), (9, 15)}}


@pytest.fixture
def engine():
    instance = hg.Grepper(os.path.abspath('tests/data/Action/Call.py'))
    return instance


def test_call(engine):
    engine.add_constraints(hg.Action.Call())
    assert results == set(engine.get_all_results())
