from ..utils import action, results_formatter
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


def test_With(grepper, action):
    action.reset()
    action.With.consideration = True
    grepper.add_constraint(action)
    assert set(grepper.get_all_results()) == all_results


def test_With_As(grepper, action):
    action.reset()
    action.With.As.consideration = True
    grepper.add_constraint(action)
    assert set(grepper.get_all_results()) == results_formatter({(1, 0)})


@pytest.mark.parametrize(('name', 'result'), [
    ('f', {(1, 0)}),
    ('g', set([]))
])
def test_With_As_name(grepper, action, name, result):
    action.reset()
    action.With.As.name = name
    grepper.add_constraint(action)
    assert set(grepper.get_all_results()) == results_formatter(result)
