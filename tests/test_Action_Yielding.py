from collections import namedtuple
import higher_grep as hg
import pytest
import os

results_template = namedtuple('Yielding', 'Line Column')

results_in_comprehension = {
    results_template(x, y)
    for x, y in {(3, 5)}
}

results_regular = {
    results_template(x, y)
    for x, y in {(8, 8)}
}

results_yield_from = {
    results_template(x, y)
    for x, y in {(12, 4)}
}


results = (results_in_comprehension | results_regular | results_yield_from)


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Yielding.py'))
    return engine


def test_Yielding(grepper):
    grepper.add_constraint(hg.Action.Yielding())
    assert results == set(grepper.get_all_results())


@pytest.mark.parametrize(('_in_comprehension'), [True, False])
def test_in_comprehension(grepper, _in_comprehension):
    grepper.add_constraint(hg.Action.Yielding(
        _in_comprehension=_in_comprehension))
    if _in_comprehension:
        assert results_in_comprehension == set(grepper.get_all_results())
    else:
        assert (results - results_in_comprehension) == set(
            grepper.get_all_results())


@pytest.mark.parametrize(('_yield_from'), [True, False])
def test_yield_from(grepper, _yield_from):
    grepper.add_constraint(hg.Action.Yielding(_yield_from=_yield_from))
    if _yield_from:
        assert results_yield_from == set(grepper.get_all_results())
    else:
        assert (results - results_yield_from) == set(grepper.get_all_results())
