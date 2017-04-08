import higher_grep as hg
import pytest
import os


def results_formatter(coordinates, name="STD_Types.py"):
    results = set([])
    for result in coordinates:
        if type(result) is hg._Result:
            results.add(result)
        else:
            results.add(hg._Result(name, result[0], result[1]))
    return results


all_results = results_formatter({
    (1, 6), (7, 8), (9, 7), (9, 18)
})


@pytest.fixture
def grepper():
    engine = hg.Grepper(
        os.path.abspath('tests/data/Kind/STD_Types.py'))
    return engine


def test_STD_Types(grepper):
    grepper.add_constraint(hg.Kind.STD_Types())
    assert set(grepper.get_all_results()) == all_results


@pytest.mark.parametrize(('_type', 'result'), [
    (str, {(7, 8), (9, 18)}),
    (int, {(1, 6)}),
    (dict, set([])),
])
def test_type(grepper, _type, result):
    grepper.add_constraint(hg.Kind.STD_Types(_type=_type))
    assert set(grepper.get_all_results()) == results_formatter(result)
