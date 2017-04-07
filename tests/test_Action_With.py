from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('With', 'Line Column')

results = {results_template(x, y) for x, y in {(1, 0), (7, 4)}}


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/With.py'))
    return engine


def test_With(grepper):
    grepper.add_constraint(hg.Action.With())
    assert results == set(grepper.get_all_results())


@pytest.mark.parametrize(('_as', 'result'), [
    ('f', {results_template(1, 0)}),
    ('g', set([]))
])
def test_with_as(grepper, _as, result):
    grepper.add_constraint(hg.Action.With(_as=_as))
    assert result == set(grepper.get_all_results())
