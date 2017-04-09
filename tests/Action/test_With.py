from ..utils import results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

all_results = results_formatter({
    (1, 0), (7, 4)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/With.py'))
    return engine


def test_With(grepper):
    grepper.add_constraint(hg.Action.With())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('_as', 'result'), [
    ('f', {(1, 0)}),
    ('g', set([]))
])
def test_with_as(grepper, _as, result):
    grepper.add_constraint(hg.Action.With(_as=_as))
    assert set(grepper.get_all_results()) == results_formatter(result)
