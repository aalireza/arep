from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Making_Nonlocal', 'Line Column')


def results_formatter(results):
    return {results_template(x, y) for x, y in results}


all_results = results_formatter({
    (3, 8), (11, 8), (14, 12)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Making_Nonlocal.py'))
    return engine


def test_Making_Nonlocal(grepper):
    grepper.add_constraint(hg.Action.Making_Nonlocal())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('_id', 'result'), [
    ('x', set(all_results - {results_template(14, 12)})),
    ('y', {(14, 12)}),
    ('z', set([]))
])
def test_id(grepper, _id, result):
    grepper.add_constraint(hg.Action.Making_Nonlocal(_id=_id))
    assert set(grepper.get_all_results()) == results_formatter(result)
