import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="Yielding.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


results_in_comprehension = results_formatter({
    (3, 5)
})

results_regular = results_formatter({
    (8, 8)
})

results_yield_from = results_formatter({
    (12, 4)
})


all_results = (results_in_comprehension | results_regular | results_yield_from)


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Action/Yielding.py'))
    return engine


def test_Yielding(grepper):
    grepper.add_constraint(hg.Action.Yielding())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('_in_comprehension'), [True, False])
def test_in_comprehension(grepper, _in_comprehension):
    grepper.add_constraint(hg.Action.Yielding(
        _in_comprehension=_in_comprehension))
    if _in_comprehension:
        assert results_in_comprehension == set(grepper.get_all_results())
    else:
        assert set(grepper.get_all_results()) == (
            all_results - results_in_comprehension
        )


@pytest.mark.parametrize(('_yield_from'), [True, False])
def test_yield_from(grepper, _yield_from):
    grepper.add_constraint(hg.Action.Yielding(_yield_from=_yield_from))
    if _yield_from:
        assert set(grepper.get_all_results()) == results_yield_from
    else:
        assert set(grepper.get_all_results()) == (
            all_results - results_yield_from
        )
