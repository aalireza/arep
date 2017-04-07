from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Making_Global', 'Line Column')


results = {
    results_template(x, y)
    for x, y in {(3, 0), (6, 4)}
}


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Making_Global.py'))
    return engine


def test_Making_Global(grepper):
    grepper.add_constraint(hg.Action.Making_Global())
    assert results == set(grepper.get_all_results())


@pytest.mark.parametrize(('_id', 'result'), [
    ('x', results),
    ('y', set([]))
])
def test_id(grepper, _id, result):
    grepper.add_constraint(hg.Action.Making_Global(_id=_id))
    assert result == set(grepper.get_all_results())
