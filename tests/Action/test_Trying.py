from ..utils import results_formatter
from functools import partial
import higher_grep as hg
import pytest
import os

results_formatter = partial(results_formatter, name=os.path.basename(__file__))

results_with_finally = results_formatter({
    (7, 0)
})

results_misc = results_formatter({
    (2, 0), (7, 0), (17, 4)
})

all_results = (results_with_finally | results_misc)


@pytest.fixture
def grepper():
    engine = hg.Grepper(os.path.abspath('tests/data/Action/Trying.py'))
    return engine


def test_Trying(grepper):
    grepper.add_constraint(hg.Action.Trying())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('_with_except_list', 'result'), [
    (IndexError, {(2, 0), (7, 0)}),
    ([IndexError, AttributeError], {(7, 0)}),
    (AttributeError, {(7, 0)}),
    (Exception, {(17, 4)})
])
def test_with_except_list(grepper, _with_except_list, result):
    grepper.add_constraint(hg.Action.Trying(
        _with_except_list=_with_except_list))
    assert set(grepper.get_all_results()) == results_formatter(result)


@pytest.mark.parametrize(('_with_except_as_list', 'result'), [
    ('e', results_with_finally),
    ('z', set([]))
])
def test_except_as_list(grepper, _with_except_as_list, result):
    grepper.add_constraint(hg.Action.Trying(
        _with_except_as_list=_with_except_as_list))
    assert set(grepper.get_all_results()) == results_formatter(result)


@pytest.mark.parametrize(('_with_finally', 'result'), [
    (True, {(7, 0)}),
    (False, (all_results - results_formatter({(7, 0)})))
])
def test_with_finally(grepper, _with_finally, result):
    grepper.add_constraint(hg.Action.Trying(_with_finally=_with_finally))
    assert set(grepper.get_all_results()) == results_formatter(result)
